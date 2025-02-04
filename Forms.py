from wtforms import Form, StringField, TextAreaField, DecimalField, validators,SubmitField

class createProductsForm(Form):
    Product_name = StringField('Product Name', [validators.DataRequired()])
    Price = DecimalField('Price', [validators.NumberRange(min=0), validators.DataRequired(message="Price is required")])
    Description = TextAreaField('Description', [validators.DataRequired()])


class updateProductsForm(Form):
    Product_name = StringField('Product Name', [validators.DataRequired()])
    Price = DecimalField('Price', [validators.NumberRange(min=0), validators.DataRequired()])
    Description = TextAreaField('Description', [validators.DataRequired()])
    submit = SubmitField('Update Product')
