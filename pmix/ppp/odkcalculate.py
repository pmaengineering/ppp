class OdkCalculate:
    def __init__(self, row):
        self.row = row

    def to_html(self):
        return ""

    def to_text(self):
        return ""

    def __repr__(self):
        return '<OdkCalculate {}>'.format(self.row['name'])
