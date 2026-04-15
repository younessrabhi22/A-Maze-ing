NAME        = a_maze_ing.py
CONFIG_FILE = default_config.txt

all: run

run:
	@python3 $(NAME) $(CONFIG_FILE)

install:
	@python3 -m pip install --upgrade pip
	@python3 -m pip install flake8 mypy build

debug:
	@python3 -m pdb $(NAME) $(CONFIG_FILE)

lint:
	@flake8 .
	@mypy . --warn-return-any --warn-unused-ignores \
	         --ignore-missing-imports --disallow-untyped-defs \
	         --check-untyped-defs --explicit-package-bases

lint-strict:
	@flake8 .
	@mypy . --strict --explicit-package-bases

build:
	@python3 -m build

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null \
		|| true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null \
		|| true
	@rm -rf build/ dist/ *.egg-info src/*.egg-info

fclean: clean
	@rm -f maze.txt

re: fclean all

.PHONY: all run install debug lint lint-strict build clean fclean re
