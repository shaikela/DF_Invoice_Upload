class Bpost:


    def __init__(self,number, weight ,awb, operation_date, from_country, to_country,from_country_zip,to_country_zip
                 ,carrier , service_type, weight_UOM, charges):
        self.number = number
        self.awb = awb
        self.weight = weight
        split = operation_date.split('-')
        self.operation_date = split[0]+split[1]+ split[2]
        self.chargeable_weight = 0
        self.amount = 0
        self.from_country = from_country
        self.from_country_zip = from_country_zip
        self.to_country = to_country
        self.to_country_zip = to_country_zip
        self.carrier = carrier
        self.service_type = service_type
        self.weight_UOM = weight_UOM
        if charges == "":
            self.charges = []
        else:
            self.charges = charges.split(',')



    def set_chargeable_weight(self, weight):
        self.chargeable_weight = weight

    def set_amount(self, amount):
        self.amount = amount