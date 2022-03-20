from .filter import ScoreFilter
import traceback

class CategoryFilter(ScoreFilter):
  def __init__(self, config):
    self.config = config

  def score(self, products):
    try:
      scores = []
      for product in products:
        if product["category"] == self.config["category"]:
          scores.append(1.0)
        else:
          scores.append(0.0)

      return scores
    except:
      traceback.print_exc()
      return [0.0] * len(products) 