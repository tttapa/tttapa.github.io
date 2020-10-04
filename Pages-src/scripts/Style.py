from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Operator, Generic, Number, Literal


class VSCodeStyle(Style):

    background_color = "#ffffff"
    default_style = ""

    styles = {
        Comment:                   "#008000",
        Comment.Preproc:           "#af00db",
        Comment.PreprocFile:       "#a31515",
        Keyword:                   "#0000ff",
        Keyword.Constant:          "#4e8ae9",
        Operator.Word:             "#0000ff",
        Keyword.Type:              "#2b91af",
        Keyword.Namespace:         "#af00db",
        String:                    "#a31515",

        Number.Bin:                "#09885a",
        Number.Float:              "#09885a",
        Number.Hex:                "#09885a",
        Number.Integer:            "#09885a",
        Number.Integer.Long:       "#09885a",
        Number.Oct:                "#09885a",

        Name.Attribute:            "#001080",
        Name.Builtin:              "#795e26",
        Name.Class:                "#2b91af",
        Name.Function:             "#795e26",
        Name.Variable:             "#0F1E87",
        Name.Constant:             "#0000FF",
        Name.Label:                "#AF00DB",
        Name.Namespace:            "#000000",

        Name.Tag:                  "#800000",

        Literal:                   "#0000FF",


        Generic.Heading:           "bold",
        Generic.Subheading:        "bold",
        Generic.Emph:              "italic",
        Generic.Strong:            "bold",
        Generic.Prompt:            "bold",

        Error:                     "border:#FF0000"
    }