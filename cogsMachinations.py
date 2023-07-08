# This is python code for COGS by jacob writen on 2023-07-07
# This code checks the Graduate Student Employment Standards page for changes

from urllib.request import urlopen
import re
import time
import os
from bs4 import BeautifulSoup


def print_hi(name, url, reference):
    articles_of_gses = read_site_data(url)
    print(f'Hi, {name}.')
    # print the site we are checking
    print(f'Retrieving {url}')
    print(f'Comparing to {reference}')
    # compare today's txt file to the reference file and print the differences

    print(articles_of_gses)

    # # print if changes were found


def read_site_data(url):
    # read in data from a site and save a copy for comparison

    # get today's date
    today = time.strftime("%Y-%m-%d")
    html_filename = f'{today} GSES.html'
    txt_filename = f'{today} GSES.txt'

    # read in the bytes
    with urlopen(url) as response:
        html = response.read()
    # decode the bytes
    html = html.decode('utf-8')

    # save html to a file
    with open(html_filename, 'w') as html_file:
        # write the date to the file
        html_file.write(html)

    # find the title <span>Graduate Student Employment Standards</span>
    title = re.search(r'<span>Graduate Student Employment Standards</span>', html)
    # find where the title starts in the html
    title_start = title.start()
    #find where the unordered list ends
    list_end = re.search(r'</ul>', html[title_start:]).start()

    # find all list elements with class="menu-item" after the title and before the end of the list
    list_items = re.findall(r'(<li class="menu-item">[\s\S]*?</li>)', html[title_start:title_start+list_end])
    articles = list()
    gses_body = 'Graduate Student Employment Standards\n\n'
    for item in list_items:
        # remove everything except the link item text
        item_text = re.search(r'<[\s\S]*>([\w\s&;:]+)</a>[\s\S]*', item).group(1)
        articles.append(item_text)
        # visit the subpage and copy the body text into today's output file
        # get the link
        sub_link = re.search(r'(/[^/]*?)"', item).group(1)
        # read in the bytes
        with urlopen(f'{url}{sub_link}') as sub_response:
            sub_page_html = sub_response.read()
            # decode the bytes
            sub_page_html = sub_page_html.decode('utf-8')
            # get the beginning and end of the div with class="clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item"
            body_start = re.search(r'<div class="clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item">', sub_page_html).end()
            #find open and close divs after the start of the body
            searching_for_closure = True
            search_start = body_start
            while searching_for_closure:
                open_divs = re.search(r'<div', sub_page_html[search_start:]).start()
                close_divs = re.search(r'</div>', sub_page_html[search_start:]).start()
                if close_divs < open_divs:
                    searching_for_closure = False
                    body_end = search_start + close_divs
                else:
                    search_start += close_divs+1

            soup = BeautifulSoup(sub_page_html[body_start:body_end], features='html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            body_text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in body_text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            body_text = '\n'.join(chunk for chunk in chunks if chunk)

            gses_body += item_text + '\n'+'-'*len(item_text)+'\n'+body_text+'\n\n'

    # write the body text to the output file
    with open(txt_filename, 'w') as txt_file:
        txt_file.write(gses_body)

    return(articles)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    web_address = 'https://grad.uiowa.edu/funding/graduate-student-employment-standards'
    # web_address = 'https://grad.uiowa.edu/academics/manual/academic-program/section-vii-graduate-appointments'
    compare_file = '2021-07-07 GSES.txt'

    print_hi('COGS', web_address, compare_file)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
