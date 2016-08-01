from bs4 import BeautifulSoup
import urllib

def find_all_permalinks(myurl, link):
    visited_links, queue = set(), [link]
    while queue:
        if len(visited_links) > 100:
            break
        new_link = queue.pop()
        if new_link not in visited_links:
            print(new_link)
            visited_links.add(new_link)
            try:
                response = urllib.request.urlopen(myurl + new_link)
            except:
                visited_links.remove(new_link)
                print('Error accessing this link:' + myurl + new_link)
            else:
                nested_file = response.read().decode('windows-1251')
                soup = BeautifulSoup(nested_file, 'html.parser')
                if soup.find_all('a'):
                    for ref in soup.find_all('a'):
                        if ref.get('href') is not None:
                            if ref.get('href').find('../') > -1 or ref.get('href').find('/') > -1:
                                queue.append(ref.get('href').replace('../', ''))
                            else:
                                fix_link = '/'.join(str.split(new_link, "/")[:len(str.split(new_link, "/")) -  1]).replace(myurl, "")
                                queue.append(fix_link + "/" + ref.get('href'))


                #    queue.extend([ref.get('href').replace('../','') if ref.get('href') is not None else '' for ref in soup.find_all('a')])
    return visited_links

myurl = 'http://ukrstat.gov.ua/operativ/'

trial_links = find_all_permalinks(myurl,'oper_new.html')

for link in trial_links:
    try:
        response = urllib.request.urlopen(myurl + link)
    except:
        print("Error accessing link: " + myurl + link)
    else:
        content = response.read().decode('windows-1251')
        soup = BeautifulSoup(content, 'html.parser')
        for table in soup.find_all('table', class_= "MsoNormalTable"):
            print(myurl + link)
            filename = soup.title.string.replace('\r\n', '')
            file = open(filename + '.txt', "w")
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                entry = ''
                for col in cols:
                   entry += col.text + ' '
                file.write(entry.replace('\n', '').replace('\r','').strip(' ') + '\n')
            file.close()


