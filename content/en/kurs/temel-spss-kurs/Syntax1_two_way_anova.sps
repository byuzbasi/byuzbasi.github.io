* Encoding: UTF-8.
MANOVA
sales BY factor1 (1 2) factor2(1 3)
/DESIGN = factor2 WITHIN factor1(1) factor2 WITHIN factor1(2)
/DESIGN = factor1 WITHIN factor2(1) factor1 WITHIN factor2(2) factor1 WITHIN factor2(3)
