#!/usr/bin/python3

import struct

class PCDToBINConverter:
    """
    Reads a PCD file (ASCII format) with fields x,y,z,(intensity) and
    writes them as float32-packed values into a .bin file.
    
    If intensity is absent in the PCD, we fill it with 0.0.
    """
    def __init__(self, pcd_file: str, output_bin: str):
        """
        :argument pcd_file: Path to the PCD file (ASCII format).
        :argument output_bin: Path to the output .bin file.
        """
        self.pcd_file = pcd_file
        self.output_bin = output_bin

        # Will be filled when parsing the header
        self.has_intensity = False
        self.num_points = 0

        # Parsed data (lists of float or None)
        self.x = []
        self.y = []
        self.z = []
        self.i = []

    def run_conversion(self):
        """
        Main entry point: parse PCD header, parse data lines, write .bin.
        """
        self._parse_pcd()
        self._write_bin()
        print(f"[PCDToBINConverter] Wrote {self.num_points} points => {self.output_bin}")

    def _parse_pcd(self):
        """
        Reads the PCD header to detect field layout and number of points.
        Then parses all data lines into self.x, self.y, self.z, self.i.
        """
        header_parsed = False
        data_section = False
        fields = []

        with open(self.pcd_file, "r") as f:
            for line in f:
                line_stripped = line.strip()

                # Once we see 'DATA ascii', the lines after are points
                if line_stripped.upper().startswith("DATA "):
                    if "ascii" not in line_stripped.lower():
                        raise NotImplementedError("Only ASCII PCD is supported in this example.")
                    data_section = True
                    header_parsed = True
                    continue

                if not data_section:
                    # Parse header lines
                    if line_stripped.startswith("FIELDS"):
                        parts = line_stripped.split()
                        # e.g. "FIELDS x y z intensity"
                        # first element is "FIELDS", so skip it
                        fields = parts[1:]
                        self.has_intensity = ("intensity" in fields)

                    elif line_stripped.startswith("POINTS"):
                        parts = line_stripped.split()
                        # e.g. "POINTS 12345"
                        self.num_points = int(parts[1])

                else:
                    # data_section == True -> lines of x,y,z,(intensity)
                    if not line_stripped:
                        continue  # skip empty lines if any

                    values = line_stripped.split()
                    if len(fields) == 4 and self.has_intensity:
                        # fields: x, y, z, intensity
                        x_val = float(values[0])
                        y_val = float(values[1])
                        z_val = float(values[2])
                        i_val = float(values[3])
                    elif len(fields) == 3 and not self.has_intensity:
                        # fields: x, y, z
                        x_val = float(values[0])
                        y_val = float(values[1])
                        z_val = float(values[2])
                        i_val = 0.0  # no intensity in PCD
                    else:
                        # If for some reason fields and actual data lines mismatch:
                        raise ValueError(
                            f"Unexpected data line: {line_stripped}. "
                            f"Fields = {fields}."
                        )

                    self.x.append(x_val)
                    self.y.append(y_val)
                    self.z.append(z_val)
                    self.i.append(i_val)

        if not header_parsed:
            raise ValueError("No DATA section found in PCD file - is it a valid ASCII PCD?")

        # Sanity check on number of points
        actual_count = len(self.x)
        if self.num_points != actual_count:
            print(f"Warning: Header said {self.num_points} points, but read {actual_count} lines.")
            self.num_points = actual_count  # Update if there's a mismatch

        if self.num_points == 0:
            raise ValueError("No points read from the PCD file.")

    def _write_bin(self):
        """
        Writes the parsed points to a .bin file as [x, y, z, intensity] float32.
        """
        with open(self.output_bin, "wb") as bin_f:
            for idx in range(self.num_points):
                # pack 4 float32 values in little-endian format
                bin_f.write(struct.pack('<ffff', 
                                        self.x[idx],
                                        self.y[idx],
                                        self.z[idx],
                                        self.i[idx]))
    


if __name__ == "__main__":
    # Example usage:
    pcd_path = "example.pcd"
    bin_path = "output.bin"
    converter = PCDToBINConverter(pcd_path, bin_path)
    converter.run_conversion()
