class OdkCalculate:
    def __init__(self, row):
        self.row = row

    def to_html(self, *args, **kwargs):
        return ""

    def to_text(self, *args, **kwargs):
        return ""

    def __repr__(self):
        return '<OdkCalculate {}>'.format(self.row['name'])
