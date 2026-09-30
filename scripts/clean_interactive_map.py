from pathlib import Path
from bs4 import BeautifulSoup


SOURCE = Path(
    "data/results/hsr_routes_highway_interactions.html"
)

OUTPUT = Path(
    "data/results/hsr_routes_clean.html"
)


def hide_panel(soup, search_text):

    search_text = search_text.lower()

    for element in soup.find_all(True):

        text = " ".join(
            element.stripped_strings
        ).strip().lower()

        if search_text not in text:
            continue

        current = element

        # Move upward until we reach a large floating container.
        for _ in range(12):

            if current is None:
                break

            style = current.get("style", "").lower()

            try:
                width = float(
                    current.get("data-width", "0")
                )
            except:
                width = 0

            # Look for fixed/absolute containers.
            if (
                "position: fixed" in style
                or "position:fixed" in style
                or "position: absolute" in style
                or "position:absolute" in style
            ):

                current["style"] = (
                    current.get("style", "")
                    + ";display:none !important;"
                )

                return True

            current = current.parent

    return False


def move_station_panel(soup):

    for element in soup.find_all(True):

        text = " ".join(
            element.stripped_strings
        ).strip().lower()

        if "station candidate search" not in text:
            continue

        current = element

        for _ in range(12):

            if current is None:
                break

            style = current.get("style", "").lower()

            if (
                "position: fixed" in style
                or "position:fixed" in style
                or "position: absolute" in style
                or "position:absolute" in style
            ):

                current["style"] = (
                    current.get("style", "")
                    + ";"
                    "top:20px !important;"
                    "right:20px !important;"
                    "left:auto !important;"
                    "bottom:auto !important;"
                    "width:360px !important;"
                    "max-height:520px !important;"
                    "overflow-y:auto !important;"
                    "z-index:9999 !important;"
                )

                return True

            current = current.parent

    return False


def remove_esri_option(soup):

    removed = False

    for element in soup.find_all(["label", "div", "span"]):

        text = " ".join(
            element.stripped_strings
        ).strip()

        if text.lower() != "esri street map":
            continue

        # Remove the individual base-map option,
        # not the complete Leaflet layer control.
        parent = element.parent

        if parent:

            parent.decompose()
            removed = True

    return removed


def add_cleanup_script(soup):

    script = soup.new_tag("script")

    script.string = r"""
(function () {

    function cleanMapUI() {

        const all = document.querySelectorAll("*");

        all.forEach(function (el) {

            const text =
                (el.innerText || "")
                .replace(/\s+/g, " ")
                .trim();

            /*
             * Remove Route Summary
             */

            if (
                text.includes("HSR Route Summary") &&
                !text.includes("Station Candidate Search")
            ) {

                let parent = el;

                for (let i = 0; i < 10; i++) {

                    if (!parent) break;

                    const style =
                        window.getComputedStyle(parent);

                    if (
                        style.position === "fixed" ||
                        style.position === "absolute"
                    ) {

                        parent.style.display = "none";
                        break;
                    }

                    parent = parent.parentElement;
                }
            }


            /*
             * Remove AHP / TOPSIS panel
             */

            if (
                text.includes(
                    "AHP & TOPSIS Decision Analysis"
                )
            ) {

                let parent = el;

                for (let i = 0; i < 10; i++) {

                    if (!parent) break;

                    const style =
                        window.getComputedStyle(parent);

                    if (
                        style.position === "fixed" ||
                        style.position === "absolute"
                    ) {

                        parent.style.display = "none";
                        break;
                    }

                    parent = parent.parentElement;
                }
            }


            /*
             * Remove Esri Street Map option
             */

            if (
                text === "Esri Street Map"
            ) {

                const parent = el.parentElement;

                if (parent) {
                    parent.style.display = "none";
                }
            }

        });


        /*
         * Move Station Candidate Search
         */

        all.forEach(function (el) {

            const text =
                (el.innerText || "")
                .replace(/\s+/g, " ")
                .trim();

            if (
                text.includes(
                    "Station Candidate Search"
                )
            ) {

                let parent = el;

                for (let i = 0; i < 10; i++) {

                    if (!parent) break;

                    const style =
                        window.getComputedStyle(parent);

                    if (
                        style.position === "fixed" ||
                        style.position === "absolute"
                    ) {

                        parent.style.top = "20px";
                        parent.style.right = "20px";
                        parent.style.left = "auto";
                        parent.style.bottom = "auto";
                        parent.style.width = "360px";
                        parent.style.maxHeight = "520px";
                        parent.style.overflowY = "auto";
                        parent.style.zIndex = "9999";

                        break;
                    }

                    parent = parent.parentElement;
                }
            }

        });

    }


    setTimeout(cleanMapUI, 500);
    setTimeout(cleanMapUI, 1500);
    setTimeout(cleanMapUI, 3000);

})();
"""

    soup.body.append(script)


def main():

    print("==========================================")
    print(" CLEANING HSR INTERACTIVE GIS MAP")
    print("==========================================")

    if not SOURCE.exists():

        raise FileNotFoundError(
            f"Original map not found:\n{SOURCE}"
        )

    html = SOURCE.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    # 1. Hide Route Summary
    if hide_panel(
        soup,
        "HSR Route Summary"
    ):
        print("✓ HSR Route Summary removed")
    else:
        print("⚠ Route Summary not found")


    # 2. Hide AHP/TOPSIS
    if hide_panel(
        soup,
        "AHP & TOPSIS Decision Analysis"
    ):
        print("✓ AHP/TOPSIS panel removed")
    else:
        print("⚠ AHP/TOPSIS panel not found")


    # 3. Move Station Search
    if move_station_panel(soup):
        print(
            "✓ Station Candidate Search moved to right"
        )
    else:
        print(
            "⚠ Station Candidate Search not found"
        )


    # 4. Remove Esri option
    if remove_esri_option(soup):
        print(
            "✓ Esri Street Map option removed"
        )
    else:
        print(
            "⚠ Esri option not found"
        )


    # 5. Add browser-side cleanup as backup
    add_cleanup_script(soup)

    OUTPUT.write_text(
        str(soup),
        encoding="utf-8"
    )

    print()
    print("✓ CLEAN MAP CREATED")
    print()
    print(OUTPUT.resolve())
    print("==========================================")


if __name__ == "__main__":
    main()