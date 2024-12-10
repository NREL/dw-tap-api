

def summary_to_html(lat, lon, closest_height, powercurve, mean, ws_level, kwh_produced_avg_year, version="latest"):

    if version == "latest":
        # This version is based on:https://codepen.io/mrsahar/pen/yOVGBQ
        # (one of tabled styles listed at: https://devdevout.com/css/css-tables, authored by: Sahar Ali Raza)

        html = """
        <p class="results_text">Analysis presented below was performed using
        summary data from <strong>NREL's 20-year
        <a href="https://www.energy.gov/eere/wind/articles/new-wind-resource-database-includes-updated-wind-toolkit" target="_blank" rel="noopener noreferrer">NREL's WTK-LED dataset</a></strong> using the following options:
        <!-- <sup>*</sup> --!>
        </p>
        <br>
    	<ul class="results_text">
        	        <li>Selected location (lat, lon): <strong>%.5f, %.5f</strong></li>
                    <li>Selected hub height: <strong>%.1f meters</strong></li>
                    <li>Selected power curve: <strong>%s</strong></li>
        </ul>
        <div id="generic_price_table">
        <section>
                <div class="container">

                    <!--BLOCK ROW START-->
                    <div class="row">
                        <div class="col-md-4">

                        	<!--PRICE CONTENT START-->
                            <div class="generic_content clearfix">

                                <!--HEAD PRICE DETAIL START-->
                                <div class="generic_head_price clearfix">

                                    <!--HEAD CONTENT START-->
                                    <div class="generic_head_content clearfix">

                                    	<!--HEAD START-->
                                        <div class="head_bg"></div>
                                        <div class="head">
                                            <span>Average wind speed</span>
                                        </div>
                                        <!--//HEAD END-->

                                    </div>
                                    <!--//HEAD CONTENT END-->

                                    <!--PRICE START-->
                                    <div class="generic_price_tag clearfix">
                                        <span class="price">
                                            <span class="currency">%.2f</span>
                                        </span>
                                    </div>
                                    <!--//PRICE END-->

                                </div>
                                <!--//HEAD PRICE DETAIL END-->

                                <!--FEATURE LIST START-->
                                <div class="generic_feature_list">
                                	<ul>
                                    	<li><span>m/s, </span> meters per second</li>
                                    </ul>
                                </div>
                                <!--//FEATURE LIST END-->

                            </div>
                            <!--//PRICE CONTENT END-->

                        </div>

                        <div class="col-md-4">

                        	<!--PRICE CONTENT START-->
                            <div class="generic_content clearfix">

                                <!--HEAD PRICE DETAIL START-->
                                <div class="generic_head_price clearfix">

                                    <!--HEAD CONTENT START-->
                                    <div class="generic_head_content clearfix">

                                    	<!--HEAD START-->
                                        <div class="head_bg"></div>
                                        <div class="head">
                                            <span>Wind Resource</span>
                                        </div>
                                        <!--//HEAD END-->

                                    </div>
                                    <!--//HEAD CONTENT END-->

                                    <!--PRICE START-->
                                    <div class="generic_price_tag clearfix">
                                        <span class="price">
                                            <span class="sign">level:  </span>
                                            <span class="currency">%s</span>
                                        </span>
                                    </div>
                                    <!--//PRICE END-->

                                </div>
                                <!--//HEAD PRICE DETAIL END-->

                                <!--FEATURE LIST START-->
                                <div class="generic_feature_list">
                                	<ul>
                                    	<li>based on average wind speed</li>
                                    </ul>
                                </div>
                                <!--//FEATURE LIST END-->


                            </div>
                            <!--//PRICE CONTENT END-->

                        </div>
                        <div class="col-md-4">

                        	<!--PRICE CONTENT START-->
                            <div class="generic_content clearfix">

                                <!--HEAD PRICE DETAIL START-->
                                <div class="generic_head_price clearfix">

                                    <!--HEAD CONTENT START-->
                                    <div class="generic_head_content clearfix">

                                    	<!--HEAD START-->
                                        <div class="head_bg"></div>
                                        <div class="head">
                                            <span>Energy Production</span>
                                        </div>
                                        <!--//HEAD END-->

                                    </div>
                                    <!--//HEAD CONTENT END-->

                                    <!--PRICE START-->
                                    <div class="generic_price_tag clearfix">
                                        <span class="price">
                                            <span class="currency">%s</span>
                                        </span>
                                    </div>
                                    <!--//PRICE END-->

                                </div>
                                <!--//HEAD PRICE DETAIL END-->

                                <!--FEATURE LIST START-->
                                <div class="generic_feature_list">
                                	<ul>
                                    	<li><span>Average kWh/year</span></li>
                                    </ul>
                                </div>
                                <!--//FEATURE LIST END-->

                            </div>
                            <!--//PRICE CONTENT END-->

                        </div>
                    </div>
                    <!--//BLOCK ROW END-->

                </div>
            </section>
        </div>
        <div>
        <p class="results_disclaimer_text"><span>
        <!-- <sup>*</sup> --!>
        Disclaimer: This summary represents a PRELIMINARY analysis.
        Research conducted at national laboratories suggests that multiple models should be used for
        more thorough analysis.
        Reach out to a qualified installer for a refined estimate.
        </span></p>
        </div>
        """ % (lat, lon, closest_height, powercurve, mean, ws_level, kwh_produced_avg_year)
        return html

    elif version == "v2":
        html = """
            <p class="results_text">Analysis presented below was done using NREL's WTK-LED dataset<sup>*</sup> and its 12x24 summaries for 2001-2020 at %d meters.</p>
            <br>
            <table border="0" cellspacing="10" class="summary_table">
            	<tbody>
            		<tr>
            			<td><span class="summary_table_metric">20-year wind speed average, m/s:</span></td>
            		</tr>
            		<tr>
            			<td><span class="summary_table_value">%.2f</span></td>
            		</tr>
            	</tbody>
            </table>
            <br>
            <p class="results_disclaimer_text"><sup>*</sup> Disclaimer: Research conducted at national laboratories suggests that multiple models should be used for
            more thorough analysis.</p>
        """ % (mean, closest_height)
        return html

    elif version == "v1":
        html = """
            <table border="0" cellspacing="10" class="summary_table">
            	<tbody>
            		<tr>
            			<td><span class="summary_table_metric">All-time wind speed average, m/s:</span></td>
            		</tr>
            		<tr>
            			<td><span class="summary_table_value">%.2f</span></td>
            		</tr>
            		<tr>
            			<td><span class="summary_table_desc">estimated using 12x24 summaries from WTK-LED<br>for 2001-2020 at %d meters.</span></td>
            		</tr>
            	</tbody>
            </table>
        """ % (mean, closest_height)

        html += """
            <hr>
            <table border="0" cellspacing="10" class="yearly_table">
            	<tbody>
            		<tr>
            			<td><span class="yearly_table_metric">Wind speed average for<br><u>lowest</u> year (%d):</span></td>
                        <td><span class="yearly_table_metric">Wind speed average for<br><u>median</u> year (%d):</span></td>
                        <td><span class="yearly_table_metric">Wind speed average for<br><u>highest</u> year (%d):</span></td>
            		</tr>
            		<tr>
            			<td><span class="yearly_table_value">%.2f</span></td>
                        <td><span class="yearly_table_value">%.2f</span></td>
                        <td><span class="yearly_table_value">%.2f</span></td>
            		</tr>
            	</tbody>
            </table>
        """ % (2008, 2010, 2012, mean*0.9, mean*1.0, mean*1.1)

        return html

    else:
        return ""


def windresource_to_html(mean, ws_level, moderate_resource_thresh_ms, high_resource_thresh_ms, closest_height, version="latest", windrose_plot_name=""):

    if version == "latest":
        # This version is based on the latest in summary_to_html()

        html = """
        <p class="results_text">The wind resource is characterized by wind speed and wind direction.
        These are both illustrated by a "wind rose" which shows how fast the wind blows from each wind direction throughout the year.
        </p>
        <br>
        <p class="results_text">
        Understanding where the wind comes from and how fast the wind blows are critical to placing the wind turbine
        in a location that will not be affected by nearby structures and trees.
        </p>
        <br>
        """

        if windrose_plot_name:
            html += """
            <div classes="centered">
            <div>
            <table>
                <tr>
                  <td><img id=\"windrose_plot\" src=\"%s\"/></td>
                </tr>
            </table>
            </div>
            </div>
            <br>
            """ % windrose_plot_name

        html += """
        <p class="results_text">
        Whether or not a specific project site is a good candidate for a wind turbine is based on several key factors including available financial incentives,
        the cost of power in the area, cost to install the turbine as well as the wind resource.  In the absence of detailed project economics,
        it is illustrative to understand whether the wind speed is generally "low", "moderate", or "high" -- which correlates directly with low, moderate or high turbine performance.
        </p>
        <br>
        """

        html +=  """
        <div id="windresource_table">
        <section>
                <div class="container">

                    <!--BLOCK ROW START-->
                    <div class="row">
                        <div class="windresource-col">

                            <!--PRICE CONTENT START-->
                            <div class="windresource_content clearfix">

                                <!--HEAD PRICE DETAIL START-->
                                <div class="windresource_head_price clearfix">

                                    <!--HEAD CONTENT START-->
                                    <div class="windresource_head_content clearfix">

                                        <!--HEAD START-->
                                        <div class="head_bg"></div>
                                        <div class="head">
                                            <span>Wind Resource</span>
                                        </div>
                                        <!--//HEAD END-->

                                    </div>
                                    <!--//HEAD CONTENT END-->

                                    <!--PRICE START-->
                                    <div class="windresource_price_tag clearfix">
                                        <span class="price">
                                            <span class="sign">level:  </span>
                                            <span class="currency">%s</span>
                                        </span>
                                    </div>
                                    <!--//PRICE END-->

                                </div>
                                <!--//HEAD PRICE DETAIL END-->

                                <!--FEATURE LIST START-->
                                <div class="windresource_feature_list">
                                	<ul>
                                        <li><span class="details_label">Details:</span></li>
                                    	<li><span>Estimated average wind speed is at %.2f m/s.</span></li>
                                        <li><span>Low</span> wind resource referts to wind speeds <span>below %.2f m/s.</span></li>
                                        <li><span>Moderate</span> wind resource refers to wind speeds <span>between %.2f and %.2f m/s.</span></li>
                                        <li><span>High</span> wind resource refers to wind speeds <span>above %.2f m/s.</span></li>
                                    </ul>
                                </div>
                                <!--//FEATURE LIST END-->

                            </div>
                            <!--//PRICE CONTENT END-->

                        </div>

                    </div>
                    <!--//BLOCK ROW END-->

                </div>
            </section>
        </div>
        <!--
            <div>
            <p class="results_disclaimer_text"><span><sup>*</sup> Disclaimer: ...</span></p>
            </div>
        --!>
        """ % (ws_level, mean, moderate_resource_thresh_ms, moderate_resource_thresh_ms, high_resource_thresh_ms, high_resource_thresh_ms) #, closest_height)
        return html
    else:
        return ""


def energyproduction_to_html(monthly_df, yearly_df):
    monthly_html = monthly_df.to_html(classes="estimates_by_month_table") # classes="detailed_yearly_table")
    yearly_html = yearly_df.to_html(classes="estimates_by_year_table") #classes="detailed_yearly_table")

    html = """
        <p class="results_text">
        The wind resource, and by extension the energy production, varies month to month and year to year.
        It is important to understand the average characteristics as well as the variability you can expect to see from your wind turbine on any given year.
        </p>
        <br>
        <!-- <p class="results_text">
        The table on the left details the wind speed and energy output for each month based on the average of 20 years at your site.
        The summary on the right gives the total energy output for the lowest and highest of 20 years as well as an average year.
        </p>
        <br>
        --!>
        <table border="0" cellspacing="10" class="yearly_table">
        	<tbody>
        		<tr>
        			<td>
                        <!-- <span class="tooltip monthly_table_tooltip"><i class="fas fa-info-circle"></i></span> -->
                        <span class="production_label">Estimates <u>by month</u>:</span>
                    </td>
                    <td>
                        <!-- <span class="tooltip yearly_table_tooltip"><i class="fas fa-info-circle"></i></span> -->
                        <span class="production_label">Estimates <u>by year</u>:</span>
                        </td>
        		</tr>
                <!-- <tr>
        			<td>The table below details the wind speed and energy output for each month<br>based on the average of 20 years at your site.</td>
                    <td>The table below gives the total energy output for the lowest and highest<br>of 20 years as well as the average year.</td>
        		</tr> --!>
        		<tr class="tr_top_align">
        			<td>%s</td>
                    <td>%s</td>
        		</tr>
        	</tbody>
        </table>
    """ % (monthly_html, yearly_html)
    return html
