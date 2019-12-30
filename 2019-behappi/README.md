![segmentation](segmented.png)

Solves this physical hexagonal puzzle by

 1. Extracting the board layout from a photo using computer vision (OpenCV).
    Tuned to work with the single included photo but should work with similar
    photos too.

 2. Virtually shuffling the pieces

 3. Finding all solutions using brute force DFS (should take about 1 second)

# Usage

 1. `pip install -r requirements.txt`
 2. `./build.sh` (make sure you have `clang++` installed)
 3. `python extract_board.py photo.jpg segmented.png board.csv`
 4. `./bin/solver < board.csv`
