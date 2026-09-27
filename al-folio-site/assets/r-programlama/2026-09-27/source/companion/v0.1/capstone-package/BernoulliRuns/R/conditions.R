.new_runs_input_error <- function(message, argument) {
  structure(
    list(message = message, call = NULL, argument = argument),
    class = c("runs_input_error", "error", "condition")
  )
}

.abort_runs_input <- function(message, argument) {
  stop(.new_runs_input_error(message, argument))
}

