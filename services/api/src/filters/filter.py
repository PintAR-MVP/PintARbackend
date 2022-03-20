from abc import ABC, abstractmethod

class QueryFilter(ABC):
  @abstractmethod
  def query(self):
    pass

class ScoreFilter(ABC):
  @abstractmethod
  def score(self, matches):
    pass
