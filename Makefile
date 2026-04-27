.PHONY: build clean run dev list

build:
	uv sync --dev
	uv run pyinstaller ipvtop.spec --clean --noconfirm

clean:
	rm -rf build dist

run: build
	sudo ./dist/ipvtop $(IFACE)

dev:
	sudo uv run ipvtop $(IFACE)

list:
	uv run ipvtop -l
