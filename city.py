import requests
from lxml import etree
from lxml.etree import _Element
import json
import re

data = requests.get('http://www.mca.gov.cn/article/sj/xzqh/2019/2019/201912251506.html')
html = etree.HTML(data.text)
table = html.xpath('//*[@id="2019年11月份县以上行政区划代码_28029"]/table')[0]
tr = table.xpath('//tr[@height="19"]')


class Element(object):
    def __init__(self, el):
        self.el = el
        self.td = el.xpath('./td')
        self.code = self.td[1].text
        self.name = self.td[2].xpath('text()')[0]

    @property
    def name_end(self):
        return self.name[-1]

    def __str__(self):
        return "{name:%s, code:%s}" % (self.name, self.code)


def parser(tr: list, length, index=0, dep=1):
    _index = index
    data = []
    while index < length:
        el = Element(tr[_index])
        if el.name_end == '省':
            if dep == 2:
                return _index - 1, data
            if dep == 3:
                return _index - 1, data
            cur_index, child_data = parser(tr, length, _index + 1, dep=dep + 2)
            data.append({
                'name': el.name,
                'code': el.code,
                'child': child_data
            })
            _index = cur_index
        elif el.name_end == '市':
            if dep == 1:
                cur_index, child_data = parser(tr, length, _index + 1, dep=dep + 1)
                data.append({
                    'name': el.name,
                    'code': el.code,
                    'child': child_data
                })
                _index = cur_index
            elif dep == 2:
                return _index - 1, data
            elif dep == 3:
                cur_index, child_data = parser(tr, length, _index + 1, 2)
                data.append({
                    'name': el.name,
                    'code': el.code,
                    'child': child_data
                })
                _index = cur_index
        elif el.name_end in ['县', '区']:
            if re.match('.*行政区$', el.name):
                if dep != 1 :
                    return _index - 1, data
                data.append({
                    'name': el.name,
                    'code': el.code
                })
            else:
                data.append({
                    'name': el.name,
                    'code': el.code
                })
        # 维护索引
        _index += 1
        if _index >= length:
            return _index, data


data = parser(tr, len(tr))
print(data)
with open('city.json', 'w+') as f:
    f.write(json.dumps(data[1], ensure_ascii=False))
