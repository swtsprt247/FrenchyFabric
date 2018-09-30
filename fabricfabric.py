from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Merchandise, Base, Categories

engine = create_engine('sqlite:///frenchy_fabric.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# fabric for merchandise
fabric1 = Merchandise(name="Fabric")

session.add(fabric1)
session.commit()

categories2 = Categories(name="Burlap", description="A coarse woven fabric made from Jute Fibers.",
                         merchandise=fabric1)

session.add(categories2)
session.commit()


categories3 = Categories(name="Canvas", description="Modern canvas is usually made of cotton or linen, although historically it was made from hemp. It differs from other heavy cotton fabrics, such as denim, in being plain weave rather than twill weave.",
                         merchandise=fabric1)

session.add(categories3)
session.commit()


categories4 = Categories(name="Chambray", description="A linen-finished gingham cloth with a white weft and a colored warp, producing a mottled appearance.",
                         merchandise=fabric1)

session.add(categories4)
session.commit()


categories5 = Categories(name="Corduroy", description="A textile with a distinct pattern, a cord or wale. Modern corduroy is most commonly composed of tufted cords, sometimes exhibiting a channel (bare to the base fabric) between the tufts. Corduroy is, in essence, a ridged form of velvet.",
                         merchandise=fabric1)

session.add(categories5)
session.commit()


categories6 = Categories(name="Denim", description="A sturdy cotton warp-faced[1] textile in which the weft passes under two or more warp threads. This twill weaving produces a diagonal ribbing that distinguishes it from cotton duck.",
                         merchandise=fabric1)

session.add(categories6)
session.commit()


categories8 = Categories(name="Eyelet", description="A lightweight fabric pierced by small holes finished with stitching and often laid out in flowerlike designs.",
                         merchandise=fabric1)

session.add(categories8)
session.commit()


categories9 = Categories(name="Faux Fur", description="A type of textile fabric fashioned to simulate genuine animal fur. It is known as a pile fabric and is typically made from polymeric fibers that are processed, dyed, and cut to match a specific fur texture and color.",
                         merchandise=fabric1)

session.add(categories9)
session.commit()


categories10 = Categories(name="Flannel", description="A soft woven fabric, of various fineness. Flannel was originally made from carded wool or worsted yarn, but is now often made from either wool, cotton, or synthetic fiber. Vegetable flannel is made from Scots pine fibre. Flannel may be brushed to create extra softness or remain unbrushed.",
                          merchandise=fabric1)

session.add(categories10)
session.commit()


categories11 = Categories(name="Fleece", description="The wool obtained from a sheep at one shearing",
                          merchandise=fabric1)

session.add(categories11)
session.commit()


categories12 = Categories(name="Rayon", description="The many types and grades of rayon can imitate the feel and texture of natural fibers such as silk, wool, cotton, and linen. The types that resemble silk are often called artificial silk.  Rayon is made from purified cellulose, primarily from wood pulp, which is chemically converted into a soluble compound. It is then dissolved and forced through a spinneret to produce filaments which are chemically solidified, resulting in fibers of nearly pure cellulose.",
                          merchandise=fabric1)

session.add(categories12)
session.commit()


# Notions for Main Page
fabric2 = Merchandise(name="Notions")

session.add(fabric2)
session.commit()


categories2 = Categories(name="Thread", description="A filament, a group of filaments twisted together, or a filamentous length formed by spinning and twisting short textile fibers into a continuous strand",
                         merchandise=fabric2)

session.add(categories2)
session.commit()


categories3 = Categories(name="Zippers", description="A device consisting of two flexible strips of metal or plastic with interlocking projections closed or opened by pulling a slide along them, used to fasten garments, bags, and other items.",
                         merchandise=fabric2)

session.add(categories3)
session.commit()


categories4 = Categories(name="Batting &amp Interfacing", description="Quilt batting is used in various sewing and quilting projects, is also known as wadding. It is used as a layer of insulation between fabrics, most often used in quilt making. Batting is the filling of quilts and makes them warm and heavy.  Interfacing creates stability for fabric.",
                         merchandise=fabric2)

session.add(categories4)
session.commit()


categories5 = Categories(name="Trim/Ribbon", description="A long, narrow strip of fabric, used especially for tying something or for decoration",
                         merchandise=fabric2)

session.add(categories5)
session.commit()


# Patterns for Main Page
fabric3 = Merchandise(name="Patterns")

session.add(fabric3)
session.commit()


categories2 = Categories(name="Women's Dresses", description="A dress can be any one-piece garment containing a skirt of any length. Dresses can be formal or informal.",
                         merchandise=fabric3)

session.add(categories2)
session.commit()


categories3 = Categories(name="Women's Tops", description="A top is an item of clothing that covers at least the chest, but which usually covers most of the upper human body between the neck and the waistline.",
                         merchandise=fabric3)

session.add(categories3)
session.commit()


categories4 = Categories(name="Handbags", description="A woman's purse.",
                         merchandise=fabric3)

session.add(categories4)
session.commit()


categories5 = Categories(name="Tote Bags", description="A large bag used for carrying a number of items.",
                         merchandise=fabric3)

session.add(categories5)
session.commit()


categories6 = Categories(name="Quilts", description="A warm bed covering made of padding enclosed between layers of fabric and kept in place by lines of stitching, typically applied in a decorative design.",
                         merchandise=fabric3)

session.add(categories6)
session.commit()


# Yarns & Crochet for Main Page
fabric4 = Merchandise(name="Yarn & Crohet")

session.add(fabric4)
session.commit()


categories2 = Categories(name="Knitting Needles", description="a long, thin, pointed rod used as part of a pair for knitting by hand.",
                         merchandise=fabric4)

session.add(categories2)
session.commit()


categories3 = Categories(name="Crochet Hooks", description="An implement used to make loops in thread or yarn and to interlock them into crochet stitches. It is basically a round shaft pointed on one end, with a lateral groove behind it",
                         merchandise=fabric4)

session.add(categories3)
session.commit()


categories4 = Categories(name="Knitting Loom", description=" The basic purpose of any loom is to hold the warp threads under tension to facilitate the interweaving of the weft threads. The precise shape of the loom and its mechanics may vary, but the basic function is the same.",
                         merchandise=fabric4)

session.add(categories4)
session.commit()


print("added categories!!!!")
