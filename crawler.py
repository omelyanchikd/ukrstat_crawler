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

#trial_links = ["operativ2007/sz/sz_u/srp_07rik_u.html"]

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
            header = -1
            header_names = []
            colspans = []
            rowspan = None
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if header > 0:
                    index = 0
                    start, end = colspans.pop(0)
                    for col in cols:
                        if col.has_attr('colspan'):
                            colspans.append((start + index, start + index + int(col['colspan'])))
                            for i in range(start + index, start + index + int(col['colspan'])):
                                header_names[i] += "_" + col.text.replace('\n',' ').replace('\r', ' ').replace('\t',' ').replace('\s', ' ')
                        else:
                            header_names[start + index] += "_" + col.text.replace('\n',' ').replace('\r', ' ').replace('\t',' ').replace('\s', ' ')
                        index += 1
                    header -= 1
                    if header == 0:
                        file.write(';'.join(header_names) + '\n')
                        header = -1
                elif is_header(cols):
                    header_names = []
                    for col in cols:
                        if col.has_attr('rowspan'):
                            header = int(col['rowspan']) - 1
                            break
                    colcount = 0
                    for col in cols:
                        if col.has_attr('rowspan'):
                            header_names.append(col.text.replace('\n',' ').replace('\r', ' ').replace('\t',' ').replace('\s', ' '))
                        else:
                            colspans.append((colcount, colcount + int(col['colspan'])))
                            for i in range(int(col['colspan'])):
                                header_names.append(col.text.replace('\n',' ').replace('\r', ' ').replace('\t',' ').replace('\s', ' '))
                        colcount += 1
                else:
                    entry = ''
                    colcount = 0
                    if rowspan is not None:
                        column, value, span = rowspan
                    else:
                        column = -1
                    for col in cols:
                        if colcount == column:
                            entry += value + ";"
                            span -= 1
                            if span == 0:
                                rowspan = None
                            else:
                                rowspan = (column, value, span)
                            colcount += 1
                        if col.has_attr('colspan'):
                            for i in range(int(col['colspan'])):
                                entry += col.text + ';'
                        elif col.has_attr('rowspan'):
                            rowspan = (colcount, col.text, int(col['rowspan']) - 1)
                            entry += col.text + ";"
                        else:
                            entry += col.text + ';'
                        colcount += 1
                    file.write(entry.replace('\n', '').replace('\r',' ').replace('\t',' ').replace('  ',' ') + '\n')
            file.close()

print(counter)