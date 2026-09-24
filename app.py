import csv
import os
import requests


from time import sleep, perf_counter
from typing import Optional




BASE = "https://apilearn.tukas.dev"
OUTPUT_DIR = "./parsing products"
MAX_RETRIES = 3
DEFAULT_RETRY_AFTER = 1  # секунд, если сервер не прислал заголовок Retry-After


def make_request(
    url: str,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
) -> requests.Response:
    """Выполняет GET-запрос с автоматическими повторными попытками при ответе 429."""
    retry_count = 0
    response = None

    while retry_count < MAX_RETRIES:
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code != 429:
            break

        retry_after = int(response.headers.get("Retry-After", DEFAULT_RETRY_AFTER))
        sleep(retry_after)
        retry_count += 1

    response.raise_for_status()
    return response


def get_categories() -> list[dict]:
    """Получает список всех категорий с API, проходя все страницы пагинации."""
    raw_categories = []
    url = BASE + "/api/categories/"

    while url:
        data = make_request(url).json()
        raw_categories.extend(data.get("results", []))
        url = data.get("next")

    return raw_categories


def get_products_by_category(slug: str) -> list[dict]:
    """Получает все товары указанной категории, проходя все страницы пагинации."""
    products = []
    params = {"category": slug}
    url = BASE + "/api/products/"

    while url:
        data = make_request(url, params=params).json()
        products.extend(data.get("results", []))
        url = data.get("next")
        params = None

    return products


def download_image(save_dir: str, image_url: Optional[str]) -> Optional[str]:
    """Скачивает изображение товара и сохраняет его в указанную папку."""
    if not image_url:
        return None

    file_name = os.path.basename(image_url)
    file_path = os.path.join(save_dir, file_name)
    print(f"Загружено изображение {file_name}")
    
    if os.path.exists(file_path):
        return os.path.abspath(file_path)

    with requests.get(image_url, stream=True, timeout=5) as response:
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    return os.path.abspath(file_path)


def write_to_csv(csv_path: str, products: list[dict]) -> None:
    """Записывает список товаров в CSV-файл. """
    try:
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                ["name", "path_to_image", "price", "quantity", "description"]
            )

            for product in products:
                writer.writerow(
                    [
                        product.get("name"),
                        product.get("path_image"),
                        product.get("price"),
                        product.get("quantity"),
                        product.get("description"),
                    ]
                )
            print(f"Данные записаны в {os.path.basename(csv_path)}")
    except OSError as e:
        print(f"Ошибка записи файла {csv_path}: {e}")


def main():
    start_time = perf_counter()
    print(f"{"#" * 15} Запуск парсера {"#" * 15}")
    categories = get_categories()[1:]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"{"#" * 15} Создал директорию {os.path.basename(OUTPUT_DIR)} {"#" * 15}")
    quantity_products = 0

    for category in categories:
        category_name = category["name"]
        category_dir = os.path.join(OUTPUT_DIR, category_name)
        os.makedirs(category_dir, exist_ok=True)
        print(f"{"#" * 15} Создал директорию {category_name} {"#" * 15}")
        products = get_products_by_category(category["slug"])
        quantity_products += len(products)
        
        for product in products:
            product["path_image"] = download_image(category_dir, product.get("image"))

        write_to_csv(os.path.join(category_dir, f"{category_name}.csv"), products)

    print(f"{"#" * 15} Парсер завершил свою работу {"#" * 15}")
    end_time = perf_counter()
    print(f"Спаршено {len(categories)} категорий", end=" ")
    print(f"{quantity_products} продукта и их изображений")
    execution_time = end_time - start_time
    if execution_time < 60:
        print(f"Скрипт работал: {execution_time:.2f} сек.")
    else:
        print(f"Скрипт работал: {execution_time / 60:.2f} мин.")


if __name__ == "__main__":
    main()