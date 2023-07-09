

boostrap.css

source: https://github.com/tcbegley/dash-bootstrap-css/tree/main/dist

about: dash-bootstrap-css is an extension of dash-bootstrap-components by also providing styling for dash-core-components.
- You can download a css stylesheet for your theme of choice from the above repository, store it in the assets folder, and use it by assigning "dash-bootstrap"
to className of a container object.
- Essentially, this extends your selected theme via dash-bootstrap-components to also include dash-core-components (but not all dcc components are supported).
- This largely solves the problem of also styling dash-core-components, which I will definitely want to use in my application (e.g. RangeSlider).


MANUAL CHANGES I HAVE MADE TO bootstrap.css:
I have replaced the following colors in order to align with Collinson branding:

#007bff (primary) > #003865 (navy blue)
#6c757d (secondary) > #4B4F54 (grey)
#dc3545 (danger) > #CE0058 (red)
#28a745 (success) > #218D7F (green)
#17a2b8 (info) > #007DBA (blue)

I had to seperately find out how to change the color of the rail of the dcc.Rangeslider:
resource: https://github.com/AnnMarieW/HelloDash/blob/main/assets/dbc_pulse.css 
(found via: https://hellodash.pythonanywhere.com/theme_explorer >>> Dash Core Components section >>> "Styling dcc.Slider and dcc.RangeSlider" >>> "see CSS")
I looked up "rc-slider-rail" in the bootstrap.css file and replaced the color with #003865 (navy blue)

I also had to seperately find out how to change the color of dcc.dropdown:
resource: https://github.com/AnnMarieW/HelloDash/blob/main/assets/dbc_dark.css
(found via: https://hellodash.pythonanywhere.com/theme_explorer >>> Dash Core Components section >>> "Styling dcc.Dropdown" >>> "see CSS")

It took me a while to change the font color of the selected values in the dropdown, but finally I realised I had to actually add the following:
.dash-bootstrap .Select-value-label {
    color: #003865 !important;
}

I also replaced the color of "dash-bootstrap .Select-menu-outer" with #003865 (navy blue): this changed the font color of items in dropdown menu.