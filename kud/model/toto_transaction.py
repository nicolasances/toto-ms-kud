
class TotoTransaction: 

    id: str
    date: int
    description: str
    amount: float
    year_month: str

    def __init__(self, id, date, description, amount, year_month):
        self.id = id
        self.date = date
        self.description = description
        self.amount = amount
        self.year_month = year_month