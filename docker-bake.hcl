group "default" {
  targets = ["main"]
}

target "main" {
  context    = "."
  dockerfile = "./Dockerfile"

  tags = [
    "yoniash/open_university_student_performance:latest"
  ]

  platforms = ["linux/amd64", "linux/arm64"]
}

