use reqwest::blocking::Client;
use reqwest::header;
use scraper::{Html, Selector};
use std::io::Write;
use url::Url;

pub fn find_articles() -> String {
    let mut headers = header::HeaderMap::new();
    headers.insert(header::USER_AGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36".parse().unwrap());
    headers.insert(
        header::ACCEPT,
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            .parse()
            .unwrap(),
    );
    headers.insert(header::ACCEPT_LANGUAGE, "en-US,en;q=0.5".parse().unwrap());
    headers.insert(header::DNT, "1".parse().unwrap());
    headers.insert(header::CONNECTION, "close".parse().unwrap());

    let client = Client::new();

    let urls: String = search("AAPL", &client);

    let doc = Html::parse_document(&urls);
    let selector = Selector::parse("a").unwrap();

    let mut count = 0;

    for e in doc.select(&selector) {
        count += 1;
        let tmp = std::fs::OpenOptions::new()
            .write(true)
            .append(true)
            .open("data.txt")
            .unwrap();

        write!(&tmp, "{}\n", e.attr("href").expect("link not found")).expect("unable to write");
    }

    println!("{}", count);

    return urls;
}

fn search(query: &str, client: &Client) -> String {
    let url = Url::parse(format!("https://news.google.com/search?q={}+stock", query).as_str())
        .expect("error");

    let mut headers = header::HeaderMap::new();
    headers.insert(header::USER_AGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36".parse().unwrap());
    headers.insert(
        header::ACCEPT,
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            .parse()
            .unwrap(),
    );
    headers.insert(header::ACCEPT_LANGUAGE, "en-US,en;q=0.5".parse().unwrap());
    headers.insert(header::DNT, "1".parse().unwrap());
    headers.insert(header::CONNECTION, "close".parse().unwrap());

    let response: String = client
        .get(url)
        .headers(headers)
        .send()
        .unwrap()
        .text()
        .unwrap();

    return response;
}
