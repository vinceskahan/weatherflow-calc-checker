#!/usr/bin/python
#
# calculate WF derived measurements using their published formulas
# note: this is written for python 2.7
#
# changelog
#     2018-10-26 - WF user @vinceskahan
#

import sys
import math

###########################################
#
# my location altitude in feet, with offsets for sensor heights
#
Esky = (358.4 + 10.5) * 0.3048  # sky elevation in m
Eair = (358.4 + 4.0)  * 0.3048  # air elevation in m

###########################################
#
# data from the WF app 2018-10-26
#
T       = 14.8     # air temp degC          (observed)
Psta    = 1002.0   # station pressure mbar  (observed)
Psea    = 1015.3   # sealevel pressure mbar (WF app)
H       = 93       # relative humidity pct  (observed)
Dp      = 13.7     # dewpoint degC          (WF app)
Twb     = 14.1     # wet bulb temp degC     (WF app)
Tdelta  = 0.7      # deltaT degC            (WF app)
AD      = 1.21234  # air density kg/m3      (WF app)

print
print "------ input data ------"
print "T      degC   observed         = " , T 
print "Psta   mb     observed         = " , Psta
print "Psea   mb     WF calculated    = " , Psea
print "H      pct    observed         = " , H
print "Dp     degC   WF calculated    = " , Dp
print "Twb    degC   WF calculated    = " , Twb
print "Tdelta degC   WF calculated    = " , Tdelta
print "AD     kg/m3  WF calculated    = " , AD
print "Eair   m      user defined     = " , Eair
print "Esky   m      user defined     = " , Esky
print


###########################################

# from weatherflow derived formulas page
def calcDeltaT(T,Twb):
    float(T)
    float(Twb)
    return T-Twb
print "--- verify calculated deltaT matches WF app reported value ---"
print "calculated  deltaT (degC) =", calcDeltaT(T,Twb)
print "weatherflow deltaT (degC) =", Tdelta
print

###########################################

# from weather flow derived formulas page pointing to:
# http://andrew.rsmas.miami.edu/bmcnoldy/Humidity.html
#   see 'spreadsheet-ready equations' for TD

def calcDewPoint(t,h):
    T = float(t)
    H = float(h)
    Td = (243.04 * (math.log(H/100) + ( (17.625*T)/(243.04+T))) / \
         (17.625 -  math.log(H/100) - ( (17.625*T)/(243.04+T))) )
    return Td

print "--- verify calculated dewpoint matches WF app reported value ---"
print "RSMAS       dewpoint (degC) = ", calcDewPoint(T,H)
print "weatherflow dewpoint (degC) = ", Dp
print
 
###########################################
#
print "skip feels like (for now)"
print "skip heat index (for now)"
print "skip pressure trend (no historical data)"
print "skip rain rate (no historical data)"
print
#
###########################################

# equation (6) from AMS - "An Example of Uncertainty in Sea Level Pressure Reduction"
# https://journals.ametsoc.org/doi/full/10.1175/1520-0434%281998%29013%3C0833%3AAEOUIS%3E2.0.CO%3B2

def calcSealevelPressure(e,p):
    Eair=float(e)     # configured elevation of air in m
    Psta=float(p)     # reported station pressure mb

    P0 = 1013.25      # std sealevel pressure mb
    Rd = 287.05       # gas const for dry air J/kg*K
    GammaS = 0.0065   # std atmos lapse rate K/m
    g = 9.80655       # gravity m/sec2
    T0 = 288.15       # std sealevel temp K
   
    # too ugly to do it on one line and keep any clarity
    part1 = P0 / Psta
    exp1  = (Rd * GammaS) / g

    part2 = (GammaS * Eair) / T0
    exp2  = g/(Rd * GammaS)

    Psea = Psta * math.pow( ( 1 + (math.pow(part1,exp1) * part2) ), exp2)

    return Psea

print "--- verify calculated sealevel pressure matches WF app reported value ---"
print "weatherflow AWS formula sealevel pressure (mb) = ", calcSealevelPressure(Eair,Psta)
print "weatherflow reported    sealevel pressure (mb) = ", Psea
print

###########################################

print "--- verify calculated vapor pressure matches WF app reported value ---"

# weatherflow formula from derived formulas page
#  - note this uses observed temperature and observed humidity
#  - why is this different from the referenced weather.gov formula ?
def calcVaporPressureWF(t, h):
    T = float(t)  # degC
    H = float(h)  # pct
    E = (H / 100) * 6.112 * math.exp((17.67 * T) / (243.5 + T));
    return E;
print "weatherflow calculated vapor pressure (mb) =" , calcVaporPressureWF(T, H)

# weather.gov vapor pressure pointed to from WF derived formulas page
#  - note this uses calculated dewpoint
#
#   https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf
#   https://www.iap.tuwien.ac.at/www/surface/vapor_pressure 
#   https://www.weather.gov/epz/wxcalc_vaporpressure 
#
def calcVaporPressure(t):
    T = float(t)
    E = 6.11 * math.pow(10, ((7.5 * T) / (237.3 + T)));
    return E;
print "weather.gov saturated  vapor pressure (mb) =" , calcVaporPressure(Dp)

# this is probably a bit silly, as here we're calculating humidity from
# observed temperature and a calculated dewpoint that was calculated 'from'
# observed temperature and 'observed' humidity.  We've already verified
# the WF dewpoint calculation above, but this perhaps might validate the
# 'for a bonus answer' part of the weather.gov page referenced above
#
print
print "--- verify derived humidity matches WF app reported value ---"
print "weather.gov rel humidity (pct) =" , int( 100 * calcVaporPressure(Dp) / calcVaporPressure(T) )
print "observed    rel humidity (pct) =" , H

###################################

# air density in kg/m3
# ref: https://wahiduddin.net/calc/density_altitude.htm (4b)
def airDensityFromIdealGasLaw(t,p):
    T  = float(t) + 273.15    # convert degC => degK
    P  = 100 * float(p)       # convert mb   => Pascals
    N  = 287.05               # specific gas constant , J/(kg*degK) = 287.05 for dry air
    return P/(N * T)
print
print "--- verify air_density matches WF app reported value ---"
print "ideal gas law calculated air_density  =", airDensityFromIdealGasLaw(T,Psta)
print "weatherflow reported air_density      =", AD
print

