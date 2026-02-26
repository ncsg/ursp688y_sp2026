# Urban Data Science & Smart Cities
**URSP688Y**<br>
**Spring 2026**<br>
Urban Studies and Planning<br>
School of Architecture, Planning, and Preservation<br>
University of Maryland, College Park

**Instructor**<br>
Chester Harvey<br>
National Center for Smart Growth<br>
[cwharvey@umd.edu](cwharvey@umd.edu)

This repository contains files and other course content for URSP688Y, *Urban Data Science and Smart Cities*, in Spring 2026. It will be updated regularly throughout the semester. Official announcements, readings, and grades will be handled on [ELMS-Canvas](https://umd.instructure.com/courses/1402425).

Students should submit all assignments as pull requests to this repository. All submitted materials will be public.

## Quick Links & Overview
|Week|Topic|Format|Due|Discussion Leader
|:--|:--|:--|:--|:--|
|[Week 1: Jan 29](#january-29-week-1)|*Class Canceled for Snow*|***NO CLASS***||-|
|[Week 2: Feb 5](#february-5-week-2)|Course Introduction & Programming Fundamentals|[Zoom](https://umd.zoom.us/j/95813351606)||Chester|
|[Week 3: Feb 12](#february-12-week-3)|Tabular Analysis|***In-Person***|Exercise 0|Emmanuel|
|[Week 4: Feb 19](#february-19-week-4)|Modular Programming and Generalizability|[Zoom](https://umd.zoom.us/j/95813351606)|Exercise 1|Derek|
|[Week 5: Feb 26](#february-26-week-5)|Accessing and Wrangling Data|[Zoom](https://umd.zoom.us/j/95813351606)|Exercise 1 Code Review|Finn|
|[Week 6: Mar 5](#march-5-week-6)|Geospatial Data|[Zoom](https://umd.zoom.us/j/95813351606)|Exercise 2|Dominic|
|[Week 7: Mar 12](#march-12-week-7)|Data Visualization|***In-Person***|Exercise 2 Code Review|Chester|
|[Spring Break](#march-19-spring-break)| 🏄 🌴 🏄 🌴 🏄 🌴 🏄 🌴 |***NO CLASS***||-|
|[Week 8: Mar 26](#march-26-week-8)|Final Project Proposal Workshop|[Zoom](https://umd.zoom.us/j/95813351606)|Final Project Proposal|-|
|[Week 9: Apr 2](#april-2-week-9)|Network Analysis|[Zoom](https://umd.zoom.us/j/95813351606)||Xuedi| 
|[Week 10: Apr 9](#april-9-week-10)|Spatial Visualization|***In-Person***|Exercise 3|Siddhi|
|[Week 11: Apr 16](#april-16-week-11)|Dashboards|[Zoom](https://umd.zoom.us/j/95813351606)|Exercise 3 Code Review|Colin|
|[Week 12: Apr 23](#april-23-week-12)|Machine Learning|[Zoom](https://umd.zoom.us/j/95813351606)||Noah|
|[Week 13: Apr 30](#april-30-week-13)|Final Project Code Review Workshop|[Zoom](https://umd.zoom.us/j/95813351606)|Exercise 4|Joseph|
|[Week 14: May 7](#may-7-week-14)|Final Project Presentations|***In-Person***|Final Project Slides|-|
|[Week 15: May 14](#may-14-week-15)|Final Project Due|***NO CLASS***|Final Project Report|-|

## Technology

[Zoom Room](https://umd.zoom.us/j/95813351606)

### Websites

[GitHub](https://github.com/ncsg/ursp688y_sp2026) (Coding demos and exercises)

[ELMS-Canvas](https://umd.instructure.com/courses/1402425) (Readings, grades, and course communications)

### Equipment

You will need a Mac, Windows, or Linux laptop with the ability install software and join a Zoom meeting, preferably with a camera. If you have challenges accessing appropriate technology, please let me know and I will try to help.

## Course Description

Novel data and computational tools are reshaping planning, development, operation, and understanding of urban systems. These may enable more efficient and equitable distribution of resources but may also reproduce injustices and divert attention away from more straightforward solutions. This course will introduce students to basic tools and applications in data science for examining urban systems while also challenging them to critique the role of technology in improving cities. What are data science’s strengths and weaknesses? Where does it belong (or not) in our planning toolkits? Have planners and technologists appropriately espoused the capabilities of data science and smart cities? How have these technologies failed to live up to their advertised capabilities? What questions can big data answer, and what issues does it raise? These overarching questions will guide parallel technical and theoretical threads throughout the semester.

The technical thread will use coding demos and short exercises to introduce students to programming logic and Python for urban data science. Demos will be aimed at beginners: students who have never coded before. Exercises will give beginners opportunities to practice new skills and more advanced coders opportunities to address urban applications they may not have previously encountered.

The theoretical thread will use reading seminars to examine the emergence, capabilities, and limitations of smart cities, big data, and urban data science.

The threads will converge on a final project that asks students to use data science to address a contemporary planning issue and critique its capabilities and limitations. Students may either implement their project in code or write a detailed proposal for it.

This course will prepare you to:

1. Use programming logic and Python to address analytical questions, implement analyses, and share them reproducibly with industry-standard tools
2. Understand the technical and ethical limitations of digital technologies in urban contexts
3. Be professionally conversant with urban technologies, either as a coder or collaborator in design, implementation, and interpretation of urban analyses

## Components

### Coding Demos

Each class will include an interactive coding demo. In addition to introducing core techniques, these will be an opportunity to roll up our sleeves and program collaboratively as a class. They will show how programming is sometimes (or often) messy and frustrating, but achievable with a bit of grit and ingenuity. Demos will be a welcoming place for beginner coders to embrace uncertainty, ask what might feel like dumb questions, and recognize that many others are facing the same challenges.

### Reading Seminars

Each class will also include a discussion-based reading seminar. You should complete readings _ahead_ of each class and be prepared to discuss them. Readings demonstrate the use of urban data science techniques in research and discuss theoretical issues around the use of urban data science and smart cities technologies. They are meant to show both best practices _and_ opportunities for critique and improvement.

Everyone will be assigned to lead discussion for at least one class. Discussion leaders should pose questions to classmates and manage discussion about issues raised by the readings. Leaders should _not_ give presentations summarizing the readings.

### Exercises (30% of grade)

Short exercises and complementary code reviews will give you opportunities to practice coding and review how your classmates address the same problems. Each exercise will be structured around a question addressable with the techniques you have learned so-far. You are encouraged to outline solutions with pseudocode. Good pseudocode will get 90% credit, even without runnable code.

A “clean result” means that I can rerun your code and arrive at the same number, table, figure, or other final output that you did, and that this output addresses the question posed by the exercise. There will rarely be entirely right or wrong answers.

Each exercise will be followed by a code review assignment in which you will be assigned to review the solution submitted by a classmate. Here are some guidelines for code review, adapted from John Ousterhout’s [Software Design Studio](https://web.stanford.edu/~ouster/cs190-winter24/) at Stanford University:

- Write approximately 5-15 comments, depending on code complexity and issues/strengths.
- Focus on red flags, including issues with flow, logic, documentation.
- Is the code easily understandable? Could you use or adapt it? Identify the most complicated parts.
- How effective are variables and functions? Too generalized? Not generalized enough?

Late submissions will automatically receive a 10% penalty for each day they are overdue with a maximum late penalty of 50%.

Exercises and code reviews will be submitted as pull requests and comments on the [course GitHub repository](https://github.com/ncsg/ursp688y_sp2024).

**Note that all pull requests and comments on the course repo will be publicly viewable.**

Exercises \[and code reviews\] will be graded out of 10 points based on this rubric:

- 0: nothing handed in
- 6: sloppy or illogical code or pseudocode with no clean result  
    \[offers perfunctory praise or identifies basic issues\]
- 9: sloppy code with a clean result OR neat and logical pseudocode  
    \[identifies key strengths and issues\]
- 10: neat and logical code or pseudocode with a clean result  
    \[thorough evaluation of strengths and issues\]
- 11: wow

### Final Project (50% of grade)

The course will culminate with a final project delivered in three stages—a short proposal (10%), presentation (10%), and final product (30%)—that uses data science to address a real-world planning problem. You may do the final project independently or with one partner.

The project will ask you to address a request from an imaginary planning agency for analysis of a potential equity gap within their city or region. You will choose which agency you are working for and the question you are asking about equitable outcomes. In designing your analysis and discussing the results, you should also consider the theoretical strengths and weaknesses of using data science and smart city approaches to examine equity and address inequities.

Projects may take two forms: (1) a functioning analysis with input data and a codebase that yield reproducible results, or (2) a proposal for an analysis that could reasonably be executed.

#### Functional Analysis

You will develop a well-documented repository of data and code, along with a short accompanying narrative describing the project’s motivation, central question, approach, results, and discussion of their meaning. The narrative may be either a traditional paper or a customized webpage/site/app that combines text and graphics. Narratives for this option are expected to be 1,000–1,500 words (2–3 pages, single spaced).

#### Proposal

You will write a paper with sections similar to the narrative described above, but with considerably more detail about the proposed approach. In lieu of conducting the analysis, you must convincingly portray how it will be conducted (when it is funded, of course), including proposed data sources and tools. The proposal should also include expanded discussion of smart cities theory to support and critique how your approach relates to equity, both in the substantive question it addresses and opportunities or issues it raises methodologically. This will likely draw on literature outside of what is assigned for the course. Narratives for this option are expected to be 4,000–6,500 words (8–12 pages, single spaced).

Convincing proposals are crucial in both research and practice. Imagine you are applying for a grant to fund a research project or responding to an RFP issued by a public agency. In both cases, you need to convince the reader that your approach is actionable. It should also be intelligible for a non-expert audience. Writing with this combination precision and clarity is a valuable skill to hone.

#### Project Components

##### 0. Proposal Pitch (In-Class March 26th; 1 slide)

Make a single slide to pitch your project idea to your classmates. Consider including:

1. Working title that explains what the project is trying to accomplish or the question it is addressing (e.g., "Are rents higher in neighborhoods with more trees?")
3. Potential data sources and key steps in analysis (high-level pseudocode)
4. Major limitations

##### 1. Short Proposal (Due March 26th; 500–1,000 words)

Write a short proposal with the following sections outlining your proposed project:

1. Introduction: What is the issue you are trying to address? Why is addressing it important? How will data science/smart cities tools help you address it?
2. Brief Background (not a full literature review): Situate the problem in the context of other work, either in practice or research. Is the place you're working in already doing something related?
3. Objectives: What specific question will your analysis answer (narrower than the issue described in the introduction)? Are you testing a hypothesis, or looking to develop theory in a spaces that lacks it?
4. Methods: What data will you need? What methods will you use to analyze these data?
5. Limitations and Ethics: How will your data and methods limit your conclusions? What ethical challenges may be posed by your analysis? What are the theoretical strengths and weaknesses of using your approach?
6. References (not included in word count): Bibliographic list of any cited works, datasets, or other materials.

Please submit on ELMS as a PDF.

##### 2. Presentation (In-Class May 7th)

Please focus your presentation on these areas:

1. Problem statement and central question
2. Data and methods used to address
3. What do the conclusions mean? (not just the results, but their _implications_)
4. What challenges and limitations are posed by using your approach? How did you address any of these challenges?

In addition to your in-class presentation, please submit slides on ELMS as a PDF.

##### 3. Final Product (Due May 14th; see above for recommended lengths and formats)

Please submit on ELMS as a PDF with links to online content, as appropriate.

### Participation (20% of grade)

This is a hands-on, discussion-oriented course. Please come to class on time having read assigned materials and ready to engage with your fellow students. Lack of engagement in and preparedness for discussion, or substantial absence, will impact your participation grade.

## Required Reading

We will read large portions of Jennifer Clark’s book on smart cities, _Uneven Innovation_. You may want to buy a hard copy, or you can read the [ebook](https://ebookcentral.proquest.com/lib/umdcp/reader.action?docID=5763883) through the UMD library. All other readings are either available at links in the schedule or on ELMS-Canvas.

Clark, J. (2020). _Uneven Innovation: The Work of Smart Cities_. Columbia University Press. ([UMD Link](https://ebookcentral.proquest.com/lib/umdcp/reader.action?docID=5763883))

## Professional Communication

Please use this course as an opportunity to practice professional communication with me and your student colleagues. Follow professional etiquette in email correspondence. Grammarly has an [excellent guide](https://www.grammarly.com/blog/email-etiquette-rules-to-know/). Please call me “Chester”; note that other professors may prefer more formal titles. Introduce your preferred pronouns—mine are he/him/his—and refer to others by their preferred pronouns.

I typically read and send email during regular business hours: 9am to 5pm ET on weekdays. I aim to address time-sensitive email within one business day but may take longer. If you send me an email on Friday, I may not get back to you until the next week. Please plan ahead.

## Zoom Guidelines­­­—‘Cameras On’ Norm

On Zoom, we will have a ‘cameras on’ norm to promote focus and collegiality. Many of us will have unideal environments or technological hiccups. This is okay. Nonetheless, please do your best to minimize distractions for you and your classmates.

## Code Readability

A key aspect of writing good code is readability: can you and others quickly and easily understand it? In many cases, code will run (readable to the machine) without being readable for a human. But sloppy, unreadable code won’t be as useful for debugging, recycling, and documenting your process. I will demonstrate readable code in demos and exercise notebooks. You will need to write readable code to get full points on exercises. You will be much more appealing as a prospective collaborator or hire if you write readable code.

UC Berkeley’s introductory computer science course, [CS61A](https://cs61a.org/articles/composition/), has an excellent composition guide. [PEP 8](https://peps.python.org/pep-0008/) is a standard Python style guide. [Google](https://google.github.io/styleguide/pyguide.html) publishes their internal Python style guide. When in doubt, be consistent and use good judgement.

## AI Policy

Generative AI is a powerful tool that is especially useful for coding. I, therefore, encourage you to learn to use it productively and responsibly as a complement to your own expertise. **You are allowed to use AI tools in any portion of this class, but you are ultimately responsible for the quality of work produced under your name. Please approach AI cautiously. I encourage you to practice transparency about where and how you use it and understand the professional consequences of using it or not.**

My personal use of AI is strongly informed by three considerations. I urge you to consider them as well.

1. ***How will my reputation be impacted if my audience knows or suspects I have used AI?***

In the academic sphere, I believe my reputation would suffer greatly, potentially even making me unemployable, if I was suspected of using AI to produce written works beyond traditional spelling and grammar check. Because of this, I make a point of never using AI for writing, and I also consider whether my own writing could have the appearance of being AI generated due to its style. I want to be trustworthy as a non-AI voice.

Conversely, I understand there are different professional norms for coding, for which copying between open sources is more well-accepted. Strictly avoiding AI as a coder might be professionally damaging. Whether AI is an asset or a liability has a lot to do with your audience and its professional norms.

2. ***What expertise do I need to use AI effectively?***

A paradox of generative AI is that it may be most valuable when used by someone who is already an expert. Senior coders can use AI to quickly assemble building blocks that might have otherwise been written by more junior colleagues. But who will replace the senior coders if we no longer need junior staff? Without as much compulsory training by doing, it is more important than ever to be diligent about your own professional development, challenging yourself to build the expertise you will need to use AI effectively rather than using it to avoid learning.

3. ***How easily could I detect an error in an AI output and how easily could I repair it?***

I avoid using AI when it would be difficult for me to detect an error or difficult for me to repair it. Of course, the difficulty of detecting and repairing is associated with expertise, so I am less likely to use AI in situations where I am less of an expert. This framework of detectability/verifiability and repairability for considering the appropriateness of AI applications was developed by Drs. Katie Shilton and Joel Chan of the [Values-Centered AI](https://vcai.umd.edu/) project in the UMD College of Information.

## Grading

Final letter grades will be assigned based on these ranges: 90-100%: A, 80-89%: B, 70-79%: C, 60-69%: D, 0-59%: F. Letters may be augmented by + or – at the high or low end of each range.

## Accessibility and Disability Services

The University of Maryland is committed to creating and maintaining a welcoming and inclusive educational, working, and living environment for people of all abilities. The University of Maryland is also committed to the principle that no qualified individual with a disability shall, on the basis of disability, be excluded from participation in or be denied the benefits of the services, programs, or activities of the University, or be subjected to discrimination. The [Accessibility & Disability Service (ADS)](https://www.counseling.umd.edu/ads/) provides reasonable accommodations to qualified individuals to provide equal access to services, programs and activities. ADS cannot assist retroactively, so it is generally best to request accommodations several weeks before the semester begins or as soon as a disability becomes known. Any student who needs accommodations should contact me as soon as possible so that I have sufficient time to make arrangements.

For assistance in obtaining an accommodation, contact Accessibility and Disability Service at 301-314-7682, or email them at [adsfrontdesk@umd.edu](mailto:adsfrontdesk@umd.edu). Information about [sharing your accommodations with instructors, note taking assistance](https://www.counseling.umd.edu/ads/currentads/) and more is available from the [Counseling Center](http://counseling.umd.edu/ads/).

## Notice of Mandatory Reporting

Notice of mandatory reporting of sexual assault, sexual harassment, interpersonal violence, and stalking:  As a faculty member, I am designated as a “Responsible University Employee,” and I must report all disclosures of sexual assault, sexual harassment, interpersonal violence, and stalking to UMD’s Title IX Coordinator per University Policy on Sexual Harassment and Other Sexual Misconduct.  

If you wish to speak with someone confidentially, please contact one of UMD’s confidential resources, such as [CARE to Stop Violence](https://health.umd.edu/CARE) (located on the Ground Floor of the Health Center) at 301-741-3442 or the [Counseling Center](https://counseling.umd.edu/) (located at the Shoemaker Building) at 301-314-7651.

You may also seek assistance or supportive measures from UMD’s Title IX Coordinator, Angela Nastase, by calling 301-405-1142 or emailing [titleixcoordinator@umd.edu](mailto:titleixcoordinator@umd.edu).

To view further information on the above, please visit the Office of Civil Rights and Sexual Misconduct's website at [ocrsm.umd.edu](http://ocrsm.umd.edu/).

## Other University Policies

Please see UMD’s [website for graduate course-related policies](https://gradschool.umd.edu/course-related-policies).

## Useful References

### Other Courses

_Structure and Interpretation of Computer Programs_ (CS61A), UC Berkeley. <https://cs61a.org/>

_Introduction to Computer Science_ (CS50), Harvard. <https://www.edx.org/cs50>

_Introduction to Data Science_ (CMSC320), UMD. <https://cmsc320.github.io/>

Courses listed below under “Acknowledgements”

### Books

Adhikari, A., DeNero, J., Wagner, D. (2022) _Computational and Inferential Thinking: The Foundations of Data Science_, 2<sup>nd</sup> Edition. <https://inferentialthinking.com> (Originally developed as the textbook for Data 8: Foundations of Data Science, UC Berkeley)

Downey, A. B. (2012). _Think Python: How to Think Like a Computer Scientist - 2e_. Green Tea Press. <https://greenteapress.com/wp/think-python-2e/>

Lloyd, C. D. (2010). _Spatial Data Analysis: An Introduction for GIS Users_. Oxford University Press. ([UMD Link](https://app-knovel-com.proxy-um.researchport.umd.edu/kn/resources/kpSDAAIGI8/toc))

Rey, S., Arribas-Bel, D., & Wolf, L. J. (2023). _Geographic Data Science with Python_. CRC Press. <https://geographicdata.science/book/intro.html>

Singleton, A. D., Spielman, S., & Folch, D. (2018). _Urban Analytics._ SAGE Publications Ltd.

Ousterhout, J. (2021). _A Philosophy of Software Design_, 2<sup>nd</sup> Edition. Yaknyam Press. ([PDF Link](https://milkov.tech/assets/psd.pdf))

### Websites

Urban Informatics and Visualization [Course Wiki](https://github.com/mxndrwgrdnr/UCB_CYPLAN255_2024/wiki) (UC Berkeley)

[Software Carpentry](https://software-carpentry.org/lessons/) (Scientific computing tutorials)

[Real Python](https://realpython.com/) (Python tutorials)

## Acknowledgements

This course is inspired by numerous other courses and colleagues, especially:

- [Urban Informatics and Visualization](https://github.com/mxndrwgrdnr/UCB_CYPLAN255_2024) at UC Berkeley: Max Gardner, Paul Waddell, Meiqing Li, Irene Farah, Geoff Boeing, Sam Maurer, Arezoo Besharati, and others.
- [Introduction to Urban Data Analytics](https://www.cp101.org/) at UC Berkeley: Karen Chapple, Irene Farah, Abby Cochran, Manual Santana Palacios, and others.
- [Urban Data Science](https://urbandatascience.its.ucla.edu/) at UCLA: Adam Millard-Ball
- [Spatial Data and Analytics](https://docs.google.com/document/d/1oC10pjyeBQTenQazCpaB8Lx1b5PC1SR3WFiPgCtXqcs/edit) at UC Berkeley: Solomon Hsiang, Jonathan Proctor, Ian Bolliger, Luna Huang, and others.
- [Software Design Studio](https://web.stanford.edu/~ouster/cs190-winter24/) at Stanford University: [John Ousterhout](http://www.stanford.edu/~ouster)

## Schedule

### January 29 (Week 1)
- Class Cancled for Snow :(

### February 5 (Week 2)

- Course introduction
  - Why data science?
  - Why _urban_ data science?
  - Opportunities and challenges
  - Plan for the semester
- Level setting
  - Experience in planning/urban systems
  - Experience with programming/data/technology
- Programming fundamentals
  - Problem decomposition
    - Inputs and outputs
    - Flow and logic
    - Modular design/encapsulation
  - Incremental development
  - Pseudocode
  - Logical flow
  - Functions
  - Building and troubleshooting
    - Documentation
    - Googling
    - Generative AI
- Intro to Python
  - Why Python?
  - Variables
  - Syntax vs. style
  - Basic data types
  - Conditions and loops
- Version control and code sharing
  - Submitting exercises with GitHub
- Development environment
  - Conda
  - VS Code
  
- Reading seminar
  - Somers, J. (2023). Begin End: A coder on the waning days of the craft. _New Yorker_, 99(38), 14-18. ([Direct Link](https://www.newyorker.com/magazine/2023/11/20/a-coder-considers-the-waning-days-of-the-craft)) ([UMD Link](https://web-p-ebscohost-com.proxy-um.researchport.umd.edu/ehost/detail/detail?vid=7&sid=acd05f73-fc24-46b8-84dd-909174c20503%40redis&bdata=JnNpdGU9ZWhvc3QtbGl2ZQ%3d%3d#AN=173542209&db=ulh))
  - Chapter 1: “Uneven Innovation: The Evolution of the Urban Technology Project” (pp. 1–30) Clark, J. (2020). _Uneven Innovation_… ([UMD Link](https://ebookcentral.proquest.com/lib/umdcp/reader.action?docID=5763883))

### February 12 (Week 3)

***IN PERSON***

- Tabular Analysis
  - Table structure
    - Tidy data
    - Wide vs. Long
  - Packages
  - Numpy
  - Pandas
  - Tabular joins
  - Loading and exporting files
- Code Review Workshop (How-To)
- Reading seminar
  - Wilson, G., Aruliah, D. A., Brown, C. T., Hong, N. P. C., Davis, M., Guy, R. T., Haddock, S. H. D., Huff, K. D., Mitchell, I. M., Plumbley, M. D., Waugh, B., White, E. P., & Wilson, P. (2014). Best Practices for Scientific Computing. _PLOS Biology_, _12_(1), e1001745. <https://doi.org/10.1371/journal.pbio.1001745>

### February 19 (Week 4)

- Modular programming and generalizability
  - Writing and importing modules
  - Repository structure
- Code Review Workshop
- Reading seminar
  - Kitchin, R. (2014). The real-time city? Big data and smart urbanism. _GeoJournal_, _79_(1), 1–14. <https://doi.org/10.1007/s10708-013-9516-8>

### February 26 (Week 5)

- Accessing and wrangling data
  - APIs
  - Parsing JSON
  - Messy data
  - Big data
- Reading seminar
  - Chapter 3: “Smart Cities as Emerging Markets” (pp. 57–94)  
        Clark, J. (2020). _Uneven Innovation_… ([UMD Link](https://ebookcentral.proquest.com/lib/umdcp/reader.action?docID=5763883))

### March 5 (Week 6)

- Geospatial data
  - Points, linestrings, and polygons
  - Coordinate systems
  - Shapely
  - Geopandas
  - Overlay and proximity analyses
  - Spatial joins
- Code Review Workshop
- Reading seminar
  - Peng, Q., Knaap, G., & Finio, N. (2023). Do Multifamily Unit Rents Increase in Response to Light Rail in the Pre-service Period? _International Regional Science Review_, 01600176231162563. <https://doi.org/10.1177/01600176231162563>

### March 12 (Week 7)

***IN PERSON***

- Data visualization
  - Principles of graphic communication
  - Matplotlib
  - Seaborn
  - Export to Illustrator
- Reading seminar
  - [Chapter 1: "Graphical Excellence" pp. (13–51)] Tufte, E. R. (2001). _The Visual Display of Quantitative Information, 2nd Ed._ (2nd edition). Graphics Press.

### March 19 (Spring Break)

- Spring Break

### March 26 (Week 8)

- Final Project Proposal Workshop

### April 2 (Week 9)

- Network analysis
- Reading seminar
  - Pereira, R. H. M. (2019). Future accessibility impacts of transport policy scenarios: Equity and sensitivity to travel time thresholds for Bus Rapid Transit expansion in Rio de Janeiro. _Journal of Transport Geography_, _74_, 321–332. <https://doi.org/10.1016/j.jtrangeo.2018.12.005>

### April 9 (Week 10)

***IN PERSON***

- Spatial visualization
  - Map design fundamentals
  - Basemaps
  - Mapping in Python
- Code Review Workshop
- Reading seminar
  - Hatch, M. E., Raymond, E. L., Teresa, B. F., & Howell, K. (2023). A data feminist approach to urban data practice: Tenant power through eviction data. _Journal of Urban Affairs_, _0_(0), 1–20. <https://doi.org/10.1080/07352166.2023.2262629>

### April 16 (Week 11)

- Dashboards
- Reading seminar
  - Owusu, F., Huberts, A., Moore, D., Hecht, A., & Quinney, S. (2025). Can Targeting Messages to High-Risk Drivers Prevent Future Citations and Crashes? Evidence from a Randomized Pilot in Washington, DC. The Lab DC, District of Columbia Government. <https://thelabprojects.dc.gov/high-risk-drivers>

### April 23 (Week 12)

- Machine learning
  - Supervised and unsupervised learning
  - Classification
- Reading seminar
  - Kandt, J., & Batty, M. (2021). Smart cities, big data and urban policy: Towards urban analytics for the long run. _Cities_, _109_, 102992. <https://doi.org/10.1016/j.cities.2020.102992> 

### April 30 (Week 13)

- \[lab space held for a student-requested topic\]
- Code Review Workshop
- Reading seminar
  - Goodspeed, R. (2022). Leveraging the promise of smart cities to advance smart growth. In _Handbook on Smart Growth_ (pp. 307–322). Edward Elgar Publishing. <https://www.elgaronline.com/edcollchap/book/9781789904697/book-part-9781789904697-31.xml>

### May 7 (Week 14)

***IN PERSON***

- Final project presentations

### May 14 (Week 15)

- Final project due
