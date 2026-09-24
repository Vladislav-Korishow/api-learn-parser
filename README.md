# API Learn Parser

A Python parser for the educational website [API Learn](https://apilearn.tukas.dev/).

The program retrieves product categories and products from the website's API, downloads product images, and saves the collected data into CSV files.

## Features

* Retrieves all product categories through the API.
* Handles API pagination automatically.
* Retrieves all products for each category.
* Downloads product images and saves them locally.
* Creates a separate directory for each category.
* Saves product information to CSV files using `;` as the delimiter.
* Stores the following product data:

  * Name
  * Image path
  * Price
  * Quantity
  * Description
* Automatically retries requests when the API returns HTTP `429 Too Many Requests`.
* Measures and displays the total execution time.

## Output Structure

After running the program, the `parsing products` directory is created:

```text
parsing products/
├── Category 1/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── Category 1.csv
├── Category 2/
│   ├── image3.jpg
│   ├── image4.jpg
│   └── Category 2.csv
└── ...
```

Each CSV file contains the collected product information and local paths to downloaded images.

## Technologies

* Python
* Requests
* CSV
* REST API
* File system operations

## Purpose

This project was created as a practical Python learning project to practice working with APIs, HTTP requests, pagination, JSON data, file handling, CSV files, image downloading, error handling, and performance measurement.
