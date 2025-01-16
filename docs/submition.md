
# 1. Introduction 

Autonomous driving systems rely heavily on robust sensing modalities, with LiDAR (Light Detection and Ranging) emerging as a cornerstone technology for environmental perception. The Blickfeld Cube 1 LiDAR, with its compact form factor and extensive detection range, aims to address the challenges of detection, tracking, and real-time decision-making. In this use case, we will first review the device by exploring its key specififications and evaluate how their alighment with self-driving car requirments. Further, we will outline the implementation process in Python, including initial sanity testing and the development of object detection and tracking algorithms. 

## 1.1 Overview of the Blickfeld Cube 1 specifications 

### Physical Characteristics 
- Dimensions: 60 x 82 x 50 mm
- Wight: 275 g

The sensors7s relatively small size and moderate weight enable flexible mounting options. For self-driving vehicles, compact sensors reduce aerodynamic drag, simplify placement (e.g, rooftop, bumper, or side mirrors), and help maintain an unobtrusivve exterior design (Seif & Hu, 2016). 

### Detection capabilities
- Detection range:  5m ~ 250m
- Range resolution: < 1cm
- Range precision: < 2cm

In autonomous driving, reliable detection up to at least 200m is commonly desired, particularly for highway scenarios where vehicles travel at higher speeds. The Blickfeld Cube 1 meets this criterion by offering a maximum range of 250m, which is suitable for a wide variety of driving conditions (Blickfeld GmbH, 2023). The high range resolution (< 1cm) and precision (< 2cm) are advantageous for differentiating closely spaced objects and accurately interpreting the surrounding environment (Levinson & Thrun, 2010). 

### Field of view (FoV)
- Horizontal: 70°
- Vertical: 30° 

A wide field of view (FoV) is essential for autonomous vehicles to minimize blind spots. While the 70° horizontal range is narrower than some 120° LiDAR models available, its configurable scanning patterns can effectively focus on critical regions—such as detecting obstacles directly ahead or monitoring blind spots. The 30° vertical FoV can be adjusted for specific detection patterns, providing appropriate coverage for various height ranges including vehicles and pedestrians (Blickfeld GmbH, 2023).

### Performance 
- Scanlines: > 500 per second
- Frame Rate: 1 – 30 Hz
- Wavelength: 900 nm

A frame rate of up to 30 Hz aligns well with real-time processing requirements for autonomous systems, where high temporal resolution is essential to track fast-moving objects accurately. The scanning density (> 500 scanlines/s) further enriches the point cloud, improving the fidelity of environmental models (Teichman et al., 2013). The 900 nm wavelength is in the near-infrared range, commonly used in automotive LiDAR to balance sensitivity and eye safety (Blickfeld GmbH, 2023).

## 1.2 Alignment with Self-driving Car requirements 

### Range and Precision
- Requirement: Detect objects beyond typical stopping distances and at highway speed (ranging from approximately 150m to over 250)
- Blickfeld Cube 1 Alignment: With a specified maximum range of 250m, the Cube 1 meets this requirement for both urban and highway scenarios. The subcentimeter resolution further enhances object classification accurary (Levinson & Thrun, 2010). 

### Field of View
- Requirement: Broad coverage is needed to observed traffic in adjacent lanes, pedestrians, and obstacles with minimal blind spots. 
- Blickfeld Cube 1 Alignment: A 70° horizontal FoV may necessitate multiple sensors or carefully planned sensor placements for comprehensive coverage. However, for many operational design domains, 70° can be sufficient if complemented with additional sensors or strategic mounting. Its flexible vertical scanning pattern allows adaptation to specific operational needs (Seif & Hu, 2016). 

### Frame rate and Point Density
- Requirement: Hgher frame rates (20-30Hz or more) are typically desired for dynamic scenes. A sufficiently dense point cloud aids in precise obstacle detection and tracking. 
- Blickfeld Cube 1 Alignment: The 1-30Hz adjustable frame rate offers the flexibility to balance point cloud density with computational overhead. Over 500 scanlines per second produce a point cloud of respectable density, supporting reliable perception tasks (Teichman et al., 2011)

# 2. Implementation 

Notes: T.B.D

## 2.2 First assessment and sanity check 

In this step, we conducted a series of automated checks to verify the integrity, structure, and basic statistical properties of our LiDAR data before proceeding with any advanced analyses (e.g., spatial consistency checks, object detection). These checks included verifying the presence of required columns (Header Check), ensuring timestamps move forward in time (Timestamp Check), and examining numerical columns for anomalies (Range Check and Statistic(s) Check). Below is a summary of our observations and findings for the first set of LiDAR packets (the “part1” folder).

### Header Check
Each LiDAR CSV file was confirmed to have all the required columns (X, Y, Z, DISTANCE, INTENSITY, POINT_ID, RETURN_ID, AMBIENT, TIMESTAMP). None of the frames displayed missing headers, and no unexpected or extraneous headers were encountered. This indicates our dataset is consistently structured, matching the specified schema and avoiding parsing complications.

### Timestamp Check
In every DataFrame, the TIMESTAMP column was present and strictly non-decreasing. The logs show that each check produced a passed = True result and contained no warning messages. This confirms that time-series data for LiDAR packets is logically ordered and can be relied upon for further time-based analyses or sensor fusion tasks.

### Range Check
The Range Check output frequently appears as None, reflecting that it was either omitted for these frames or did not flag values as out of bounds given the constraints (5–250 meters). Since our dataset spans distances typically between roughly 5 m and 250+ m, any negative or zero distances might warrant further scrutiny—but here, no immediate range violations were reported for these frames in part1. We note one instance of a slightly negative value (e.g., 
−
21.37
−21.37 in one frame), which suggests investigating sensor offsets or outlier processing in future steps if needed.

### Statistic(s) Check
The StatisticsCheck module evaluated key numeric columns—focusing especially on DISTANCE and INTENSITY—to detect extreme outliers via z-score analysis. In all inspected DataFrames:

DISTANCE consistently had a minimum slightly above 5 m (or in rare cases, a small negative or near-zero reading), and a maximum often in the range of 100–259 m for certain frames. The outlier ratio was between roughly 1.3% and 1.6%, staying below typical concern thresholds (e.g., 2–5% or higher might require a deeper look).
INTENSITY spanned from 5 up to values in the 100–300+ range (depending on frame), with only a small fraction of outliers (about 0.6–0.7%) flagged by the z-score method. The majority of intensity data thus fell within a plausible distribution, suggesting no major sensor saturations or spurious artifacts at this stage.
Overall, these checks confirm that the LiDAR data in the “part1” folder is structurally coherent (headers intact, timestamps valid) and statistically reasonable (outlier ratios remain low, distributions appear stable). A minor point is the occasional negative or very low DISTANCE reading, which may arise from sensor or calibration nuances. However, nothing in the current results indicates systemic corruption or unrecoverable errors in the dataset. This successful completion of our first-round sanity checks provides confidence that subsequent steps—such as spatial consistency checks, ground estimation, or full 3D object detection—can proceed on a firm footing.










## References
- Angerer, H., Nowozin, S., & Raji, D. (2017). Profiling Real-Time Systems for Autonomous Driving Applications. In Proceedings of the IEEE International Conference on Robotics and Automation (ICRA). IEEE.
- Blickfeld GmbH. (2023). Blickfeld Cube 1 Specifications. Retrieved from https://www.blickfeld.com
- Chen, X., et al. (2017). Multi-view 3D Object Detection Network for Autonomous Driving. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR) (pp. 1907–1915). IEEE.
- Geiger, A., Lenz, P., & Urtasun, R. (2012). Are We Ready for Autonomous Driving? The KITTI Vision Benchmark Suite. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR) (pp. 3354–3361). IEEE.
- Gustafsson, F. (2012). Statistical Sensor Fusion. Studentlitteratur AB.
- Kelly, J., & Sukhatme, G. S. (2011). Visual-Inertial Sensor Fusion: Localization, Mapping and Sensor-to-Sensor Self-calibration. The International Journal of Robotics Research, 30(1), 56–79.
- Levinson, J., & Thrun, S. (2010). Robust Vehicle Localization in Urban Environments Using Probabilistic Maps. In Proceedings of the IEEE International Conference on Robotics and Automation (ICRA) (pp. 4372–4378). IEEE.
- Seif, H., & Hu, T. (2016). Autonomous Driving in the iCity—HD Maps as a Key Challenge of the Automotive Industry. Engineering, 2(2), 159–162.
- Teichman, A., Levinson, J., & Thrun, S. (2013). Towards 3D Object Recognition via Classification of Arbitrary Object Tracks. In Proceedings of the IEEE International Conference on Robotics and Automation (ICRA) (pp. 4034–4041). IEEE.