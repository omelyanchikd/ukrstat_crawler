from bs4 import BeautifulSoup
import urllib
import csv

def find_all_permalinks(myurl, link):
    good_links, visited_links, queue = set(), set(), [link]
    while queue:
        if len(good_links) > 10:
            break
        new_link = queue.pop()
        if new_link not in visited_links:
            print(new_link)
            visited_links.add(new_link)
            try:
                response = urllib.request.urlopen(myurl + new_link)
            except:
                print('Error accessing this link:' + myurl + new_link)
            else:
                good_links.add(new_link)
                nested_file = response.read().decode('windows-1251', 'replace')
                soup = BeautifulSoup(nested_file, 'html.parser')
                if soup.find_all('a'):
                    for ref in soup.find_all('a'):
                        if ref.get('href') is not None:
                            if ref.get('href').find('zip') > -1:
                                continue
                            if ref.get('href').find('../') > -1 or ref.get('href').find('/') > -1:
                                queue.append(ref.get('href').replace('../', ''))
                            else:
                                fix_link = '/'.join(str.split(new_link, "/")[:len(str.split(new_link, "/")) -  1]).replace(myurl, "")
                                queue.append(fix_link + "/" + ref.get('href'))                #    queue.extend([ref.get('href').replace('../','') if ref.get('href') is not None else '' for ref in soup.find_all('a')])
    return good_links

def is_header(columns):
    for column in columns:
        if not column.has_attr('colspan') and not column.has_attr('rowspan'):
            return False
    return True

myurl = 'http://ukrstat.gov.ua/operativ/'

trial_links = find_all_permalinks(myurl,'oper_new.html')
counter = 1

trial_links = ["operativ2007/sz/sz_u/srp_07rik_u.html"]

for link in trial_links:
    try:
        response = urllib.request.urlopen(myurl + link)
    except:
        print("Error accessing link: " + myurl + link)
    else:
        content = response.read().decode('windows-1251','replace')
        soup = BeautifulSoup(content, 'html.parser')
        for table in soup.find_all('table', class_= "MsoNormalTable"):
            print(soup.title.string.replace('\r\n', '').replace('*','') + ": " + myurl + link)
            #filename = soup.title.string.replace('\r\n', '').replace('\n', '').replace('\r','').replace('\t','').replace('*','') +\
            #           "_" + str(counter)
            filename = str(counter)
            counter += 1
            file = open(filename + '.csv', "w", encoding = "windows-1251", errors = "replace")
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                entry = ''
                if is_header(cols):
                    header = int(cols[0]['colspan'])
                    for col in cols:
                        if col.has_attr('rowspan'):
                            entry += col.text + ';'
                        elif col.has_attr('colspan'):
                            for row in header:
                                entry += cols[row].text + ';'
                else:
                    for col in cols:
                        if col.has_attr('colspan'):
                            for i in range(int(col['colspan'])):
                                entry += col.text + ';'
                    else:
                        entry += col.text + ';'
                file.write(entry.replace('\n', '').replace('\r',' ').replace('\t',' ').replace('  ',' ') + '\n')
            file.close()

print(counter)