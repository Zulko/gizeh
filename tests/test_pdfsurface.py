"""
Tests for Gizeh
"""

import gizeh as gz
import os


def test_pdfsurface(tmpdir):
    """Test PDFSurface class."""
    # 800x800 point image
    im_size = 800

    # Create a simple star shape with a fill
    shape = gz.star(stroke_width=0.01, fill=(0, 0, 0.3, 0.7))
    shape = shape.rotate(-3.14159265358979 / 2.0)
    shape = shape.scale((im_size - 100) // 2)
    shape = shape.translate([im_size // 2, im_size // 2])

    # Some text to throw on the shape...
    txt = gz.text("Gizeh on pdf",
                  fontfamily="Arial",
                  fontsize=50,
                  fill=(0, 0, 0),
                  xy=(im_size // 2, im_size // 2))

    # Create pdf surface
    filepath = os.path.join(str(tmpdir), "pdfsurface_test.pdf")
    s = gz.PDFSurface(filepath, im_size, im_size)
    # Draw shape on the PDF surface
    shape.draw(s)
    txt.draw(s)

    # Write file and close surface
    s.flush()
    s.finish()

    # Delete test PDF
