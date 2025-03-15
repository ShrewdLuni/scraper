import io
import csv
import json
import pandas as pd

from flask import Flask, Blueprint, render_template, redirect, url_for, flash, request, Response
from .service.opinions import create_opinion
from .service.products import create_product, get_product_with_opinions_by_id, get_products_with_opinions
from .scraper import CeneoScraper


def create_app():
    app = Flask(__name__)
    app.secret_key = "your_secret_key"

    @app.route('/')
    def home_page():
        return render_template("home.html")

    @app.route('/about')
    def about_page():
        return render_template("about.html")

    @app.route('/extract', methods=['GET', 'POST'])
    def extract_page():
        if request.method == 'POST':
            product_id = request.form.get('product_id')
            if not product_id or not CeneoScraper.is_valid(product_id):
                flash("Invalid product ID. Please enter a valid numeric ID.", "error")
                return redirect(url_for('extract_page'))
            return redirect(url_for('get_product_data', product_id=product_id))
        return render_template("extract.html")

    @app.route('/product/<product_id>', methods=['GET'])
    def get_product_data(product_id):
        try:
            product = get_product_with_opinions_by_id(product_id)
            if not product:
                product = CeneoScraper.get_product_data(product_id)
                create_product(product_id, product["product"])
                for review in product["reviews"]:
                    create_opinion(product_id, review)
                return redirect(url_for('get_product_data', product_id=product_id))
            return render_template("product.html", product=product, product_id=product_id)
        except Exception as e:
            print(e)
            flash("Invalid product ID or no reviews found!", "error")
            return redirect(url_for('extract_page'))
        
    @app.route('/products', methods=['GET'])
    def product_list():
        try:
            products = get_products_with_opinions()
            return render_template("products.html", products=products)
        except Exception as e:
            print(e)

    @app.route('/download/<product_id>/<format>', methods=['GET'])
    def download_reviews(product_id, format):
        product = get_product_with_opinions_by_id(product_id)
        
        if not product:
            flash("Product not found!", "error")
            return redirect(url_for('product_list'))

        reviews = product.get("opinions", [])
        filename = f"product_{product_id}_reviews.{format}"
        
        if format == "json":
            response = Response(json.dumps(reviews, indent=4), content_type="application/json")
        elif format == "csv" or format == "xlsx":
            si = io.StringIO()
            csv_writer = csv.writer(si)
            csv_writer.writerow(["author", "recommendation", "score", "content", 
                                "advantages", "disadvantages", "helpful_count", 
                                "unhelpful_count", "publish_date", "purchase_date"])
            for review in reviews:
                csv_writer.writerow([
                    review.get("author", ""),
                    review.get("recommendation", ""),
                    review.get("score", ""),
                    review.get("content", ""),
                    review.get("advantages", 0),
                    review.get("disadvantages", 0),
                    review.get("helpful_count", ""),
                    review.get("unhelpful_count", ""),
                    review.get("publish_date", ""),
                    review.get("purchase_date", "")
                ])
            
            if format == "csv":
                response = Response(si.getvalue(), content_type="text/csv")
            else:
                csv_data = si.getvalue()
                si_csv = io.StringIO(csv_data)
                df = pd.read_csv(si_csv)
                output = io.BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                response = Response(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            flash("Invalid format!", "error")
            return redirect(url_for('product_list'))
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    @app.route('/product/<product_id>/charts')
    def product_charts(product_id):
        return render_template("charts.html", product=get_product_with_opinions_by_id(product_id), product_id=product_id)

    return app