import simpy
import numpy as np
import random
import statistics
from sklearn.cluster import KMeans
class Body(object):
    def __init__(self, env):
        self.env = env
        self.classifier = None
        self.point_x = []
        self.point_y = []
        self.action = env.process(self.run())
        self.attack_class = None
        self.damage = 0
    def benign(self, x, y):
        self.point_x.append(x)
        self.point_y.append(y)
    def attacked(self, x, y):
        if self.classifier == None:
            self.damage += 1
            self.point_x.append(x)
            self.point_y.append(y)
            return True
        else:
            if self.attack_class == None:
                self.attack_class = self.classifier.predict([[x, y]])[0]
                self.damage += 1
                return True
            if self.attack_class == self.classifier.predict([[x, y]])[0]:
                return False
            else:
                self.damage += 1
                self.point_x.append(x)
                self.point_y.append(y)
                return True
    def run(self):
        while True:
            if self.damage == 10:
                print("TRAIN")
                self.classifier = KMeans(n_clusters = 2).fit(list(zip(self.point_x, self.point_y)))
                self.damage = 0
                self.point_x = []
                self.point_y = []
            yield self.env.timeout(1)
class Attacker(object):
    def __init__(self, env, body):
        self.body = body
        self.env = env
        self.action = env.process(self.run())
    def attack(self, x_mean, x_std, y_mean, y_std):
        x = np.random.normal(x_mean, x_std, 1)
        y = np.random.normal(y_mean, y_std, 1)
        att = self.body.attacked(x[0], y[0])
        if att:
            print("DAMAGE")
        else:
            print("NULLIFIED")
        yield self.env.timeout(1)
    def run(self):
        while True:
            yield self.env.process(self.attack(1, 1, 2, 1))
            yield self.env.timeout(0)
class Benign(object):
    def __init__(self, env, body, x, y):
        self.body = body
        self.env = env
        self.x = x
        self.y = y
        self.action = env.process(self.run())
    def benign(self, x_mean, x_std, y_mean, y_std):
        x = np.random.normal(x_mean, x_std, 1)
        y = np.random.normal(y_mean, y_std, 1)
        att = self.body.benign(x[0], y[0])       
        if att:
            print("BENIGN")
        yield self.env.timeout(1)
    def run(self):
        while True:
            yield self.env.process(self.benign(self.x, 1, self.y, 1))
            yield self.env.timeout(0)


env = simpy.Environment()
body = Body(env)
att1 = Attacker(env, body)
ben1 = Benign(env, body, 4, 5)
env.run(until=100)




