import aviary.api as av
from aviary.variable_info.variables import Aircraft as av_Aircraft
from aviary.variable_info.variables import Dynamic as av_Dynamic

# define new variables
AviaryAircraft = av_Aircraft


class Aircraft(AviaryAircraft):
    class Cost:
        COST_FLYAWAY = "aircraft:cost:flyaway"


ExtendedMetaData = av.CoreMetaData

av.add_meta_data(
    Aircraft.Cost.COST_FLYAWAY,
    units=None,
    desc="Total flyaway cost of the aircraft in USD",
    default_value=1.0e6,
    meta_data=ExtendedMetaData,
)
