from flask import Flask, render_template, request, redirect, url_for
from models import db, Products, Account, History, add_event

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///warehouse.db"
db.init_app(app)


@app.route("/")
def index():
    account = Account.query.first()
    products = Products.query.all()
    return render_template("index.html", saldo=account.balance, magazyn=products)


@app.route("/saldo", methods=["GET", "POST"])
def saldo():
    account = Account.query.first()
    if request.method == "POST":
        opcja_saldo = request.form["opcja_saldo"]
        if opcja_saldo == "dodaj":
            kwota = float(request.form["kwota"])
            # account = Account.query.first()
            account.balance += kwota
            new_event = add_event(
                "saldo",
                f" Dodano {kwota:.2f} zł, stan po operacji: {account.balance}",
            )
            db.session.add(account)
            db.session.add(new_event)
            db.session.commit()
        elif opcja_saldo == "odejmij":
            kwota = float(request.form["kwota"])
            # account = Account.query.first()
            account.balance -= kwota
            new_event = add_event(
                "saldo", f" Odjęto {kwota:.2f} zł, stan po operacji: {account.balance}"
            )
            db.session.add(account)
            db.session.add(new_event)
            db.session.commit()
        else:
            print("Nieprawidłowa opcja dla operacji saldo\n")

    return render_template("saldo.html", saldo=account.balance)


@app.route("/historia")
@app.route("/historia/<int:od>/<int:do>")
def history(od=None, do=None):
    history = History.query.all()
    if od is None and do is None:
        return render_template("history.html", history=history)
    elif od > do or od < 0 or do < 0 or do > len(history):
        return render_template(
            "history.html",
            error=f"Nieprawidłowy zakres; dozwolone wartości: od 0 do"
            f" {len(history)}",
        )
    else:
        return render_template("history.html", history=history[od:do])


@app.route("/zakup", methods=["GET", "POST"])
def purchase():
    account = Account.query.first()

    if request.method == "POST":
        if account.balance != 0:
            name = request.form["product"]
            price = float(request.form["price"])
            quantity = float(request.form["quantity"])
            purchase_cost = price * quantity
            if account.balance >= purchase_cost:
                new_product = Products(name=name, quantity=quantity, price=price)

                account.balance -= purchase_cost

                new_event = add_event(
                    "zakup",
                    f"kupiono {quantity} szt. {name} za {price:.2f}",
                )
                db.session.add(account)
                db.session.add(new_product)
                db.session.add(new_event)
                db.session.commit()
                message = (
                    f"Dokonałeś zakupu: {name} - cena:{price:.2f}, "
                    f"ilość: {quantity}. Saldo po operacji:"
                    f" {account.balance:.2f} zł"
                )
            else:
                message = f"Brak środków, zasil konto."
        else:
            message = f"Brak środków, zasil konto."
    else:
        message = f"Nie dokonano jeszcze zakupu"

    return render_template("purchase.html", message=message)


@app.route("/sprzedaż", methods=["GET", "POST"])
def sale():
    message = "Nie dokonano jeszcze sprzedaży"
    if request.method == "POST":
        product = request.form["product"]
        quantity = float(request.form["quantity"])

    return render_template("sale.html", message=message)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
