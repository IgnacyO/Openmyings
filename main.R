library(dplyr)
library(stringr)
library(ggplot2)
library(ggpubr)

# Before runnings script remember to import dataset with exported games within .xlsx file


get_counted_openings <- function(games_dataset, min_n_games=1) {
  # Gets dataframe with games counted for each unique opening in the given games dataset
  counted_openings <- as.data.frame(games_dataset %>% count(first_moves, name="games_n"))
  counted_openings <- counted_openings[counted_openings$games_n >= min_n_games, ]
  return(counted_openings[order(counted_openings$games_n, decreasing=T), ])
}

get_avg_score_and_sharpness <- function(openings_dataset, dataset) {
  # Gets extended openings dataframe with average score and sharpness for each opening
  avg_score_and_sharpness <- cbind(openings_dataset, avg_score=NA, avg_sharpness=NA)
  for (row in 1:nrow(openings_dataset)) {
    games_with_openings <- dataset %>% dplyr::filter(str_detect(first_moves, 
                                          openings_dataset[row, "first_moves"]))
    avg_score_and_sharpness[row, 3] = mean(games_with_openings$result)
    avg_score_and_sharpness[row, 4] = mean(games_with_openings$total_moves)
  }
  return(avg_score_and_sharpness)
}


draw_my_plots <- function(dataset, player_color) {
  # Draws plots for my analysis
  par(mfrow=c(1,2))
  my_plot <- ggplot(dataset, aes(fill=games_n, x=avg_score, y=first_moves)) + 
    geom_bar(stat = "identity") + 
    geom_vline(xintercept=0.5, linetype="dashed", col = "red") +
    geom_text(aes(x=avg_score + 0.05, label = round(avg_score, 3)), vjust = 0.5, colour = "#232323") +
    ggtitle(paste("Average score and number of games for openings played >= 4 times as ", player_color)) +
    xlab("Average points scored") + ylab("First 4 moves of the opening") +
    guides(fill=guide_legend(title="Number of games >= n"))
  
  my_plot2 <- ggplot(dataset, aes(fill=avg_sharpness, x=avg_score, y=first_moves)) + 
    geom_bar(stat = "identity") + 
    geom_vline(xintercept=0.5, linetype="dashed", col = "red") +
    geom_text(aes(x=avg_score + 0.05, label = round(avg_score, 3)), vjust = 0.5, colour = "#232323") +
    ggtitle(paste("Average score and sharpness for openings played >= 4 times as ", player_color)) +
    xlab("Avarage points scored") + ylab("First 4 moves of the opening") +
    guides(fill=guide_legend(title="Average sharpness >= s"))
  
  ggarrange(my_plot, my_plot2, ncol = 2, nrow = 1)
  
}

data1.games_as_white = subset(data1, color == "white")
data1.games_as_black = subset(data1, color == "black")
data1.openings_white = subset(get_counted_openings(data1.games_as_white, 4))
data1.openings_black = subset(get_counted_openings(data1.games_as_black, 4))
analysis_table_white <- get_avg_score_and_sharpness(data1.openings_white, data1)
analysis_table_black <- get_avg_score_and_sharpness(data1.openings_black, data1)

draw_my_plots(analysis_table_white, "white")
draw_my_plots(analysis_table_black, "black")