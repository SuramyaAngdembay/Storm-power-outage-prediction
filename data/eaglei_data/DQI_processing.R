#Data Quality Index Analysis

library(Hmisc)
library(dplyr)
library(ggplot2)
library(plotly)



#########################
## Load Utility Level Data
## because of privacy concerns, we are not providing the utility level data. 
## however, the script we use to aggregate from utility level data to FEMA region 
## is included here in lines 19-112 for clarity in the data processing methods. 
##########################


filename <- "Data/DQ_Utilities.xlsx"

DQI_util <- readxl::read_excel(path = filename, sheet = "enabled_only_raw")

DQI_util <- DQI_util %>% mutate(spatial_precision = spatial_precision*100,
                              success_rate = 100- error_rate,
                              percent_enabled = if_else(percent_enabled > 100, 100, percent_enabled))

DQI_util <- DQI_util %>% mutate(FEMA.region = case_when(fema == 1 ~ "I",
                                                        fema == 2 ~ "II",
                                                        fema == 3 ~ "III",
                                                        fema == 4 ~ "IV",
                                                        fema == 5 ~ "V",
                                                        fema == 6 ~ "VI",
                                                        fema == 7 ~ "VII",
                                                        fema == 8 ~ "VIII",
                                                        fema == 9 ~ "IX",
                                                        fema == 10 ~ "X"))


#FEMA REGIONS
rI <- c("CT", "ME", "MA", "NH", "RI", "VT")
rII <- c("NJ", "NY", "PR", "VI")
rIII <- c("DE", "MD", "PA", "VA", "DC", "WV")
rIV <- c("AL", "FL", "GA", "KY", "MS", "NC", "SC", "TN")
rV <- c("IL", "IN", "MI", "MN", "OH", "WI")
rVI <- c("AR", "LA", "NM", "OK", "TX")
rVII <- c("IA", "KS", "MO", "NE")
rVIII <- c("CO", "MT", "ND", "SD", "UT", "WY")
rIX <- c("AZ", "CA", "HI", "NV", "GU", "AS", "MP")
rX <- c("AK", "ID", "OR", "WA")

state_FEMA <- data.frame(state = c(state.abb,"DC", "VI", "PR"))

state_FEMA <- state_FEMA %>% mutate(FEMA.region = case_when(state %in% rI ~ "I",
                                                       state %in% rII ~ "II",
                                                       state %in% rIII ~ "III",
                                                       state %in% rIV ~ "IV",
                                                       state %in% rV ~ "V",
                                                       state %in% rVI ~ "VI",
                                                       state %in% rVII ~ "VII",
                                                       state %in% rVIII ~ "VIII",
                                                       state %in% rIX ~ "IX",
                                                       state %in% rX ~ "X"))


territories <- c("AS", "GU", "MP")

cust_coverage <- readr::read_csv("eaglei_outages/coverage_history.csv") %>% filter(!(state %in% territories)) 
colnames(cust_coverage) <- gsub("_", ".", colnames(cust_coverage))

cust_coverage <- cust_coverage %>% mutate(year = lubridate::mdy(year),
                                          year = lubridate::year(year)) 

cust_coverage <- cust_coverage %>% left_join(state_FEMA)

cust_coverage <- cust_coverage %>% 
                 group_by(FEMA.region,year) %>% 
                 summarise(max.covered = sum(max.covered, na.rm = TRUE),
                           total.customers = sum(total.customers, na.rm = TRUE)) %>%
                 mutate(cust_coverage= 100*max.covered/total.customers) %>% 
                 select(one_of(c("FEMA.region", "year", "cust_coverage", "max.covered", "total.customers")))
  
## Process and Summarize

DQI = DQI_util %>% group_by(FEMA.region, year) %>% summarise(success_rate = wtd.mean(success_rate, weights = utility_customers, na.rm = TRUE),
                                                               percent_enabled = wtd.mean(percent_enabled, weights = utility_customers, na.rm = TRUE),
                                                               spatial_precision = wtd.mean(spatial_precision, weights = utility_customers, na.rm = TRUE))

DQI <- DQI %>% full_join(cust_coverage, by = c("year","FEMA.region")) %>% mutate(fema = as.factor(FEMA.region))


###########
## rescale subcomponents
###########

srm = min(DQI$success_rate)
pem = min(DQI$percent_enabled)
ccm = min(DQI$cust_coverage)
spm = min(DQI$spatial_precision)

DQI <- DQI %>% dplyr::mutate(rs_success_rate = (success_rate-srm)/(1-srm/100),
                             rs_percent_enabled = (percent_enabled-pem)/(1-pem/100),
                             rs_cust_coverage = (cust_coverage-ccm)/(1-ccm/100),
                             rs_spatial_precision = (spatial_precision-spm)/(1-spm/100),
                             DQI = 0.4*rs_success_rate + 0.3*rs_percent_enabled + 0.2*rs_cust_coverage + 0.1*rs_spatial_precision,
                             DQI_alt = 0.25*rs_success_rate + 0.25*rs_percent_enabled + 0.25*rs_cust_coverage + 0.25*rs_spatial_precision
                             )


DQI_print <- DQI %>% select(!one_of("rs_success_rate", "rs_percent_enabled", "rs_cust_coverage", "rs_spatial_precision", "DQI_alt"))

write.csv(DQI_print, "data/DQI.csv", row.names = FALSE)


###########
## Produce Figures
###########


DQI <- readr::read_csv("data/DQI.csv")



cols = c("#fa9084", "#f2a561", "#fac678", "#faeb66", "#d7fc7e", "#8cff94", "#90f0f0", "#7db1f5", "#e092f0", "#a89bab")
rn_labs = c("I","II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")



### Components of paper Figure 3

ggplot(DQI, aes(x = year, y = success_rate, color = fema)) + geom_line(linewidth = 2) + 
  theme_minimal()+labs(title = "Success Rate", y = "Success Rate", x = "Year") + 
  scale_color_manual(values = cols, name = "FEMA Region", labels = rn_labs)

ggsave("output/Success_Rate.pdf", width = 6, height = 4)

ggplot(DQI, aes(x = year, y = percent_enabled, color = fema)) + geom_line(linewidth = 2) + 
  theme_minimal()+labs(title = "Percent Enabled", y = "Percent Enabled", x = "Year") +
  scale_color_manual(values = cols, name = "FEMA Region", labels = rn_labs)

ggsave("output/Percent_Enabled.pdf", width = 6, height = 4)

cc<- ggplot(DQI, aes(x = year, y = cust_coverage, color = fema)) + geom_line(linewidth = 2) + 
  theme_minimal()+labs(title = "Customer Coverage", y = "Customer Coverage Rate", x = "Year")+
  scale_color_manual(values = cols, name = "FEMA Region", labels = rn_labs)

ggsave("output/Customer_Coverage.pdf", width = 6, height = 4)

ggplotly(cc)

ggplot(DQI, aes(x = year, y = spatial_precision, color = fema)) + geom_line(linewidth = 2) + 
  theme_minimal()+labs(title = "Spatial Precision", y = "Spatial Precision Index", x = "Year")+
  scale_color_manual(values = cols, name = "FEMA Region", labels = rn_labs)

ggsave("output/Spatial_Precision.pdf", width = 6, height = 4)




#Summary Figure, (Fig 4)

ggplot(DQI, aes(x = year, y = DQI, color = fema)) + geom_line(linewidth = 2) + 
  theme_minimal()+labs(title = "Overall Data Quality Index", y = "DQI", x = "Year") +
  scale_color_manual(values = cols, name = "FEMA Region", labels = rn_labs)

ggsave("output/Overall_DQI.pdf", width = 9, height = 6)




