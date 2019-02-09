// Inputs: CSV file


import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;
import java.util.*;
import java.util.ArrayList;
import java.util.NoSuchElementException;
//note: you can visualize the data for a given time by opening the excel file and creating a graph for it
public class ScanIt {
	private static final String COMMA_DELIMITER = ",";
	private static final String NEW_LINE_SEPARATOR = "\n";
	private static final int EARTH_RADIUS = 6378100;
	private static final String FILE_HEADER = "Altitude,NS Wind,EW Wind";
	private static final int iterateBy = 20;

	
	//This section creates a new csv file with all of the wind speeds for a time specified by the user.
	//At the end it also does a sample test for the approximator.
	public static void main(String[] args) throws FileNotFoundException, NoSuchElementException {
		ArrayList<WindData> windy = readWindFile();
		Scanner consoleReader = new Scanner(System.in);
		FileWriter fileWriter = null;
		System.out.println("Day?");
		int day = consoleReader.nextInt();
		System.out.println("hour? ");
		int hour = consoleReader.nextInt();
		System.out.println("month? (int)");
		int month = consoleReader.nextInt();
		consoleReader.close();
		String name = "newFile_month" + month + "day" + day + "hour" + hour + ".csv";
		File f = new File(name);

		System.out.println("File name is :" + f.getName());
		System.out.println("file path is : " + f.getAbsolutePath());
		try {
			fileWriter = new FileWriter(name);
			
			fileWriter.append(FILE_HEADER.toString());
			fileWriter.append(NEW_LINE_SEPARATOR);

			for (int i = 0; i < 32452.5; i += 20) {
				fileWriter.append(String.valueOf(i));
				fileWriter.append(COMMA_DELIMITER);
				fileWriter.append(String.valueOf(approximator(windy, month, day, hour, i, true)));
				fileWriter.append(COMMA_DELIMITER);
				fileWriter.append(String.valueOf(approximator(windy, month, day, hour, i, false)));
				fileWriter.append(NEW_LINE_SEPARATOR);
			}
			System.out.println("Created successfully!!!");
		} catch (Exception e) {
			System.out.println("Error in CsvFileWriter !!!");
		} finally {
			if (fileWriter != null) try {
				fileWriter.flush();
				fileWriter.close();
			} catch (IOException e) {
				System.out.println("Error while flushing/closing fileWriter !!!");
			}
		}

//==========================Test the integration=====================
		simulation(windy, 3, 4, 6, 10, 40, 100, 30000);
	}
	
	
//THis function takes in time data and locates the wind data for that time in the wind.csv file
	public static int findDateData(ArrayList<WindData> win, int mon, int day, int hr) {
		int x = 0;
		for (int i = 0; i < win.size(); i++) {
			if (win.get(i).month == mon & win.get(i).day == day & win.get(i).hour == hr) {
				x = i;
				break;
			}
		}
		if (x == 0) {
			System.out.println("invalid date!");
			return -1;
		}
		return x;

	}

	// boolean ns returns ns approx if true and ew approx if false
	//this block finds the values surrounding a particular altitude and builds a linear function to approximate wind speeds between those two
	//data points. It then returns either the ew or ns approximation.
	public static double approximator(ArrayList<WindData> j, int mon, int day, int hr, double alt, boolean ns) {
		int k = findDateData(j, mon, day, hr);
		double approxNS = 0;
		double approxEW = 0;
		if (k != -1) {
			int count = 0;
			double lowerAlt = 0, upperAlt = 0, upperNS = 0, lowerNS = 0, upperEW = 0, lowerEW = 0;
			for (int i = 0; i < 31; i++) {
				if (alt < j.get(k + i).altitude) {
					count++;
				}
			}
			if (count == 0) {
				System.out.println("too high");
			} else if (alt < 0) {
				System.out.println("too low.");
			} else if (count == 31) {
				upperAlt = j.get(k + 30).altitude;
				upperNS = j.get(k + 30).ns;
				upperEW = j.get(k + 30).ew;
				lowerAlt = 0;
				lowerNS = 0;
				lowerEW = 0;
			} else {
				lowerAlt = j.get(k + count).altitude;
				lowerNS = j.get(k + count).ns;
				lowerEW = j.get(k + count).ew;
				upperAlt = j.get(k + count - 1).altitude;
				upperNS = j.get(k + count - 1).ns;
				upperEW = j.get(k + count - 1).ew;
			}
			if (count != 0 & alt > 0) {
				/*
				 * System.out.println(lowerAlt); System.out.println(upperAlt);
				 * System.out.println(lowerEW); System.out.println(upperEW);
				 * System.out.println(lowerNS); System.out.println(upperNS);
				 */
				double xRatio = (alt - lowerAlt) / (upperAlt - lowerAlt);
				approxNS = (upperNS - lowerNS) * xRatio + lowerNS;
				approxEW = (upperEW - lowerEW) * xRatio + lowerEW;
				// System.out.println("NS speed: " + approxNS + "EW Speed: " + approxEW);
			}
		}

		if (ns) {
			return approxNS;
		} else
			return approxEW;
	}

	// takes speed in m/s
	//THis block performs the integration of wind speeds to achieve an approximation for where the object will be located at a target 
	//altitude. It's basically a riemann sum
	public static void simulation(ArrayList<WindData> j, int mon, int day, int hr, double lat, double lon, double speed,
			double targetAlt) {
		double height = 0;
		double x = 0;
		double y = 0;
		double dt = 60;
		double t = 0;
		while (height < targetAlt) {
			height += speed * dt;
			t += dt;
			x += approximator(j, mon, day, hr, height, false) * dt;
			y += approximator(j, mon, day, hr, height, true) * dt;
		}
		lat += ((y / (2 * Math.PI * EARTH_RADIUS)) * 360);
		lon += (x / (2 * Math.PI * EARTH_RADIUS * Math.cos((lat * Math.PI) / 180))) * 360;
		System.out.println("new latitude: " + lat);
		System.out.println("new longitude: " + lon);
		System.out.println("meters travelled East/West: " + x);
		System.out.println("meters travelled North/South: " + y);
	}
//parses the wind file
	static ArrayList<WindData> readWindFile() throws FileNotFoundException {
		ArrayList<WindData> windy = new ArrayList<WindData>();
		String windFile = "wind.csv";
		File file = new File(windFile);
		Scanner scanner = new Scanner(file);
		String data = "";
		scanner.nextLine();
		System.out.println("start reading");
		do {

			data = scanner.nextLine();
			Scanner parser = new Scanner(data).useDelimiter(",");
			int one = parser.nextInt();
			int two = parser.nextInt();
			int three = parser.nextInt();
			int four = parser.nextInt();
			double five = parser.nextDouble();
			double six = parser.nextDouble();
			double seven = parser.nextDouble();
			double eight = parser.nextDouble();
			double nine = parser.nextDouble();
			WindData jimbo = new WindData(one, two, three, four, five, six, seven, eight, nine);
			windy.add(jimbo);
			parser.close();
		} while (scanner.hasNext());

		scanner.close();
		return windy;
	}
}
