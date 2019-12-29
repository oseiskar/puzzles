#include <algorithm>
#include <cassert>
#include <functional>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <map>
#include <vector>

struct HexCoord {
  int u, v;

  HexCoord rotate60() const {
    return { -v, u+v };
  }

  bool operator==(const HexCoord &other) const {
    return u == other.u && v == other.v;
  }

  HexCoord operator+(const HexCoord &other) const {
    return { u + other.u, v + other.v };
  }

  HexCoord operator-() const {
    return { -u, -v };
  }
};

struct CoordAndLabel {
  HexCoord coord;
  int label;
};

struct Piece {
  int label;
  std::vector<HexCoord> coords;

  bool operator==(const Piece &other) const {
    return label == other.label && coords == other.coords;
  }

  Piece rotate60() const {
    Piece result { label, {} };
    for (const auto &p : coords) {
      result.coords.push_back(p.rotate60());
    }
    return result;
  }

  Piece translate(HexCoord delta) const {
      Piece result { label, {} };
      for (const auto &p : coords) {
        result.coords.push_back(p + delta);
      }
      return result;
  }

  HexCoord min() const { return extent(-1); }
  HexCoord max() const { return extent(1); }

  HexCoord extent(int sign) const {
    bool first = true;
    int u, v;
    for (const auto &p : coords) {
      if (first || sign*p.u > sign*u) u = p.u;
      if (first || sign*p.v > sign*v) v = p.v;
      first = false;
    }
    return { u, v };
  }

  std::vector<Piece> symmetries() const {
    Piece p = *this;
    std::vector<Piece> result;
    for (int i=0; i<6; ++i) {
      p = p.translate(-p.min());
      for (const auto &other : result) {
        if (other == p) return result;
      }
      result.push_back(p);
      p = p.rotate60();
    }
    return result;
  }
};

class Board {
private:
  std::vector<int> data;

  static int getMax(const std::vector<CoordAndLabel> &coords, std::function<int(CoordAndLabel)> func) {
    int best;
    bool first = true;
    for (const auto &it : coords) {
      const int v = func(it);
      if (first || v > best) best = v;
      first = false;
    }
    return best;
  }

public:
  static constexpr int WALL = 0;
  static constexpr int BLANK = -1;

  const int maxU, maxV;

  Board(const std::vector<CoordAndLabel> &coords) :
    maxU(getMax(coords, [](CoordAndLabel c) -> int { return c.coord.u; })),
    maxV(getMax(coords, [](CoordAndLabel c) -> int { return c.coord.v; }))
  {
    data.resize((maxU+1)*(maxV+1), int(WALL));
    for (const auto &it : coords) {
      assert(it.label != WALL && it.label != BLANK);
      (*this)(it.coord.u, it.coord.v) = it.label;
    }
  }

  int &operator()(int u, int v) {
    assert(u >= 0 && v >= 0 && u <= maxU && v <= maxV);
    return data[v*(maxU+1) + u];
  }

  const int &operator()(int u, int v) const {
    return const_cast<Board&>(*this)(u, v);
  }

  int &operator()(HexCoord c) {
    const int u = c.u;
    const int v = c.v;
    assert(u >= 0 && v >= 0 && u <= maxU && v <= maxV);
    return (*this)(c.u, c.v);
  }

  const int &operator()(HexCoord coord) const {
    return const_cast<Board&>(*this)(coord);
  }

  bool fits(const Piece &piece, int deltaU = 0, int deltaV = 0) const {
    for (const auto &c : piece.coords) {
      const int u = c.u + deltaU;
      const int v = c.v + deltaV;
      if (u < 0 || v < 0 || u > maxU || v > maxV) return false;
      if ((*this)(u, v) != BLANK) return false;
    }
    return true;
  }

  void place(const Piece &piece, int deltaU = 0, int deltaV = 0) {
    for (const auto &c : piece.coords) {
      (*this)(c.u + deltaU, c.v + deltaV) = piece.label;
    }
  }

  void erase(const Piece &piece, int deltaU = 0, int deltaV = 0) {
    for (const auto &c : piece.coords) {
      (*this)(c.u + deltaU, c.v + deltaV) = BLANK;
    }
  }

  bool fits(const Piece &p, HexCoord delta) const {
    return fits(p, delta.u, delta.v);
  }
  void place(const Piece &p, HexCoord delta) { place(p, delta.u, delta.v); }
  void erase(const Piece &p, HexCoord delta) { erase(p, delta.u, delta.v); }

  void erase() {
    for (int v = 0; v <= maxV; ++v) {
      for (int u = 0; u <= maxU; ++u) {
        int &label = (*this)(u, v);
        if (label != WALL) label = BLANK;
      }
    }
  }

  std::vector<Piece> extractPieces() {
    std::map<int, std::size_t> pieceIndices;
    std::vector<Piece> result;

    for (int v = 0; v <= maxV; ++v) {
      for (int u = 0; u <= maxU; ++u) {
        const int label = (*this)(u, v);
        if (label != WALL && label != BLANK) {
          if (!pieceIndices.count(label)) {
            pieceIndices[label] = result.size();
            result.emplace_back(Piece { label, {} });
          }
          result[pieceIndices[label]].coords.emplace_back(HexCoord { u, v });
        }
      }
    }

    return result;
  }
};

char encodeLabel(int label) {
  if (label == Board::WALL) return ' ';
  if (label == Board::BLANK) return '.';
  if (label < 10) return '0' + label;
  label -= 10;
  constexpr int nAlpha = int('z' - 'a');
  if (label <= nAlpha) return 'a' + label;
  label -= nAlpha;
  assert(label <= nAlpha);
  return 'A' + label;
}

std::vector<CoordAndLabel> readBoard(std::istream &is) {
  std::vector<CoordAndLabel> result;
  std::string token;
  std::getline(is, token); // first line, ignored
  while (is) {
    if (!std::getline(is, token, ',')) break;
    const int u = std::stoi(token);
    std::getline(is, token, ',');
    const int v = std::stoi(token);
    std::getline(is, token, ',');
    const int label = std::stoi(token);
    result.emplace_back(CoordAndLabel { { u, v }, label });
    std::getline(is, token); // ignore rest of line
  }
  return result;
}

void printBoard(const Board &board) {
  for (int v = 0; v <= board.maxV; ++v) {
    for (int u = 0; u <= board.maxU; ++u) {
      std::cout << encodeLabel(board(u, v));
    }
    std::cout << std::endl;
  }
}

class Solver {
private:
  const std::size_t nPieces;
  Board board;
  std::vector<HexCoord> nonEmpty;
  std::vector<bool> usedMask;
  std::vector< std::vector<Piece> > pieceSymmetries;

public:
  int operationCount;
  int nSolutions;
  std::function<void(const Board &)> onSolution;

  Solver(const Board &emptyBoard, const std::vector<Piece> &pieces) :
    nPieces(pieces.size()), board(emptyBoard)
  {
    operationCount = 0;
    nSolutions = 0;

    for (int v = 0; v <= board.maxV; ++v) {
      for (int u = 0; u <= board.maxU; ++u) {
        if (board(u, v) != Board::WALL)
          nonEmpty.emplace_back(HexCoord { u, v });
      }
    }

    for (const auto &p : pieces) {
      pieceSymmetries.emplace_back(p.symmetries());
    }

    usedMask.resize(pieces.size(), false);
  }

  bool solve(int nextNonEmpty = 0) {
    const HexCoord anchor = nonEmpty.at(nextNonEmpty);
    for (std::size_t i = 0; i < nPieces; ++i) {
      if (usedMask[i]) continue;
      for (const auto &p : pieceSymmetries[i]) {
        for (const auto &coord : p.coords) {
          const auto delta = anchor + (-coord);
          operationCount++;
          if (board.fits(p, delta)) {
            board.place(p, delta);
            usedMask[i] = true;

            int nonEmptyIndex = nextNonEmpty;
            while (board(nonEmpty[nonEmptyIndex]) != Board::BLANK) {
              nonEmptyIndex++;
              if (nonEmptyIndex == nonEmpty.size()) {
                // solved!
                nSolutions++;
                if (onSolution) onSolution(board);
                break;
              }
            }

            if (nonEmptyIndex < nonEmpty.size()) {
              solve(nonEmptyIndex);
            }

            board.erase(p, delta);
            usedMask[i] = false;
          }
        }
      }
    }
    return nSolutions > 0;
  }
};

int main() {
  Board board(readBoard(std::cin));

  std::cout << " --- original board" << std::endl;
  printBoard(board);
  std::cout << std::endl;

  auto pieces = board.extractPieces();

  // shuffle (otherwise too easy)
  std::default_random_engine rng(0);
  std::shuffle(pieces.begin(), pieces.end(), rng);
  for (auto &p : pieces) {
    std::uniform_int_distribution<int> dist(0, 5);
    const int nRots = dist(rng);
    for (int i = 0; i < nRots; ++i) p = p.rotate60();
    p = p.translate(-p.min()); // normalize position
  }

  board.erase();

  Solver solver(board, pieces);
  solver.onSolution = [&solver](const Board &b) {
    std::cout << " --- solution #" << solver.nSolutions << std::endl;
    printBoard(b);
    std::cout << std::endl;
  };
  solver.solve();
  std::cout << "final operation count " << solver.operationCount << std::endl;

  return 0;
}
