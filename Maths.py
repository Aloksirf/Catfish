import statistics

class Maths:
    def modeMean(lis):
        try:
            return statistics.mode(lis)
        except:
            return statistics.median(lis)