from tex import latex2pdf

document = ur"""
     \documentclass{article}
     \begin{document}
     Hello, World!
     \end{document}
"""

pdf = latex2pdf(document)
with open('test_tab.pdf','wb') as f:
    f.write(pdf)
