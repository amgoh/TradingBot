mod webscraper;
use tokio;

//#[tokio::main]
fn main() {
    let _ = webscraper::find_articles();
    //println!("{}", &a);
}
