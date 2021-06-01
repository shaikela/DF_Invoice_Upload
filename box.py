class Box:
    def __init__(self,number, dim):
        self.number = number
        self.bpost_list = []
        self.chargeable_weight = 0
        self.dim = dim

    def add_bpost(self, bpost):
        self.bpost_list.append(bpost)


    def calc_box_weight(self):
        total_weight = 0
        for bpost in self.bpost_list:
            total_weight = total_weight + bpost.weight
        return total_weight

    def calc_chargeable_weight(self, value):
        res = 1
        split_str = self.dim.split('-')
        if len(split_str)!=3:
            print('bye')
            exit()
        for dim in split_str:
            if dim.replace('.','',1).isdigit():
                res = res * float(dim)
        self.chargeable_weight = res / value