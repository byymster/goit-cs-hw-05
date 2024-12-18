import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import re
from typing import List, Tuple
from bs4 import BeautifulSoup


def strip_html_tags(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def download_text(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return strip_html_tags(response.text)
    except requests.RequestException as e:
        print(f"Error downloading text: {e}")
        return ""


def map_words(text: str) -> List[Tuple[str, int]]:
    words = re.findall(r'\b\w+\b', text.lower())
    return [(word, 1) for word in words]


def reduce_word_counts(word_counts: List[Tuple[str, int]]) -> Counter:
    counter = Counter()
    for word, count in word_counts:
        counter[word] += count
    return counter


def parallel_map_reduce(text: str, num_threads: int = 4) -> Counter:
    words = re.findall(r'\b\w+\b', text.lower())
    chunk_size = len(words) // num_threads
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        mapped = executor.map(lambda chunk: map_words(" ".join(chunk)), chunks)

    reduced = Counter()
    for partial_result in mapped:
        reduced += reduce_word_counts(partial_result)

    return reduced


def visualize_top_words(word_counts: Counter, top_n: int = 10):
    top_words = word_counts.most_common(top_n)
    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color='skyblue')
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title(f"Top {top_n} Most Frequent Words")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()


def main():
    url = input("Enter the URL of the text file(press enter for default): ")
    if not url:
        url = "https://raw.githubusercontent.com/frike/ua-legislation/refs/heads/master/%D0%97%D0%B0%D0%BA%D0%BE%D0%BD%D0%B8/%D0%9F%D1%80%D0%BE%20%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D0%B8%D1%82%D1%83%D1%86%D1%96%D0%B9%D0%BD%D0%B8%D0%B9%20%D0%A1%D1%83%D0%B4%20%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D0%B8.txt"

    print("Downloading text...")
    text = download_text(url)
    if not text:
        print("Failed to download text. Exiting.")
        return

    print("Performing MapReduce...")
    num_threads = 4
    word_counts = parallel_map_reduce(text, num_threads)

    print("Visualizing results...")
    visualize_top_words(word_counts, top_n=10)
    print("Visualization complete.")


if __name__ == "__main__":
    main()