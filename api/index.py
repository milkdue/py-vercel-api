import requests
from bs4 import BeautifulSoup
import re
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

def generate_contribute_data(name):
    url = "https://github.com/" + name
    git_page = requests.get(url, "lxml")
    git_page.encoding = "utf-8"
    # print(git_page.text)
    soup = BeautifulSoup(git_page.text, "html.parser")
    print("----------------")
    div_wrapper_node = soup.find("div", class_="js-calendar-graph")
    print(div_wrapper_node)
    print("----------------")
    table_node = div_wrapper_node.find("table", class_="js-calendar-graph-table")
    tbody_node = table_node.find("tbody")
    tr_nodes = tbody_node.find_all("tr")

    index_map = {}

    if tr_nodes:
        for index in range(len(tr_nodes)):
            index_map[index] = []
            tr = tr_nodes[index]
            td_nodes = tr.find_all("td")
            if td_nodes:
                for td in td_nodes:
                    date = td.attrs.get("data-date")
                    aria = td.attrs.get("aria-labelledby")
                    if date and aria:
                        index_map[index].append({
                            "date": date,
                            "count": calc_count_by_id(div_wrapper_node, aria)
                        })

    return handler_data(index_map)

def calc_count_by_id(wrapper, element_id):
    node = wrapper.find("tool-tip", id=element_id)

    if node:
        return extract_number_and_text(node.text)

    return 0
def extract_number_and_text(s):
    if s.startswith("No"):
        return 0
    match = re.match(r'^(\d+)(.*)', s)
    if match:
        number = match.group(1)
        # text = match.group(2)
        return int(number)
    return None

def handler_data(index_map):
    result = []
    total = 0
    max_length = 0
    index_list = [0, 1, 2, 3, 4, 5, 6]

    for value in index_map.values():
        length = len(value)
        if length > max_length:
            max_length = length

    for index in range(max_length):
        contribute = []
        for key in index_list:
            contributes = index_map.get(key)
            if index < len(contributes):
                contribution = contributes[index]
                contribute.append(contribution)
                count = contribution.get("count")
                if count:
                    total = total + count
        result.append(contribute)

    return {
        "total": total,
        "contributions": result
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        query = path.split('?')[-1]
        params = urllib.parse.parse_qs(query)
        name = params.get("name", [""])[0]
        print(name)
        data = generate_contribute_data(name)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        return

print(generate_contribute_data("milkdue"))


