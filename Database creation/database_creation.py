from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import os
import json

def get_page_content(url, head):
  req = Request(url, headers=head)
  return urlopen(req)

def get_url_for_page(page):
    return f'https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&isSearchRequest=true&pageNumber={page}&pageSize=50&ref=srpNextPage&scopeId=C&sortOption.sortBy=relevance&refId=3dcdb84f-7441-d926-1abc-d9b84315430c'

def extract_data(url):
    car_data = get_page_content(url, head).read()
    soup = BeautifulSoup(car_data, 'html.parser')

    result = {}

    price = soup.find('span', {"data-testid": "prime-price"}).text
    result['price'] = price

    y = soup.find('div', {"class": "mde-price-rating__badge__label"}).text
    result['offer'] = y

    title = soup.find('h1', {'id': 'ad-title'}).text
    result['title'] = title

    key_feature_labels = soup.findAll('div', {'class': "key-feature__label"})
    key_feature_values = soup.findAll('div', {'class': 'key-feature__value'})

    key_features = [{"label": x.text, "value": y.text} for x, y in zip(key_feature_labels, key_feature_values)]
    result['key_features'] = key_features

    features = soup.findAll('div', {'class': "bullet-list"})
    features = [x.find('p').text for x in features]
    result['features'] = features

    tech_data = soup.find('div', {'class': 'cBox-body--technical-data'}).findAll('div', {'class': 'g-row'})
    tech_data_labels = [x.find('strong').text for x in tech_data]
    tech_data_values = [x.findAll('div')[1].text for x in tech_data]

    tech_data = [{"label": x, "value": y} for x, y in zip(tech_data_labels, tech_data_values)]
    result['tech_data'] = tech_data
    return result

def load_urls(path):
    urls = []

    for i in range(1, 25000):
        print(f"Ucitavam stranicu: {i}")
        try:
            data = get_page_content(get_url_for_page(i), head).read()
        except:
            continue
        
        soup = BeautifulSoup(data, features='lxml')

        results = soup.find_all("a", {"class": "result-item"})

        for a in results:
            urls.append(a['href'])

        if i % 100 == 0:
            f = open(path, "a")

            for url in urls:
                f.write(url + "\n")
            
            f.close()
            urls.clear()

def scrape_urls(path_to_urls, result_path):
    urls = []
    urls_count = 0
    results = []
    i = 0
    while True:
        with open(path_to_urls) as file:
            for line in file:
                urls.append(line.replace("\n", "&lang=en"))
                urls_count += 1
                if urls_count == 500:
                    break

        file.close()

        if urls_count == 0:
            break
        
        for url in urls:
            try:
                res = extract_data(url)
                results.append(res)
            except:
                continue
        
        with open(result_path, 'a') as fp:
            for res in results:
                j = json.dumps(res, indent=4)
                fp.write(j + ",\n")

        fp.close()

        results.clear()
        urls.clear()

        with open(path_to_urls) as f, open("tmp.txt", "w") as out:
            cnt = 0
            for line in f:
                if cnt >= urls_count:
                    out.write(line)
                cnt += 1

        os.remove(path_to_urls)
        os.rename("tmp.txt", path_to_urls)
        urls_count = 0
        print(f"Upisao {i+1}. 500.")
        i += 1


head = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
  'Accept-Encoding': 'none',
  'Accept-Language': 'en-US,en;q=0.8',
  'Connection': 'keep-alive',
  'refere': 'https://example.com',
  'cookie': """your cookie value ( you can get that from your web page) """
}

scrape_urls("njegos.txt", "njegos_results.txt")