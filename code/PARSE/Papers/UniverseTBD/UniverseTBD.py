import requests
import pandas as pd
from bs4 import BeautifulSoup


def download_paper(url, paper_id):
    pdf_url = url.replace('abs', 'pdf')
    response = requests.get(pdf_url)

    with open(f'{paper_id}.pdf', 'wb') as f:
        f.write(response.content)


def parse_and_save_html(file_path):
    # read the entire HTML file
    papers = pd.read_html(file_path, flavor='html5lib', header=0)[0]

    # save to csv
    papers.to_csv('papers.csv', index=False)

    # convert dataframe to a list of dictionaries
    papers_list = papers.to_dict('records')

    for paper in papers_list:
        download_paper(paper['url'], str(paper['ArxivID']))


if __name__ == '__main__':
    file_path = 'arXiv_astronomy_papers.html'  # replace this with your actual HTML file path
    parse_and_save_html(file_path)
