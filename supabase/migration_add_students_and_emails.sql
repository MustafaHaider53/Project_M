-- Migration: Add students and emails
-- Auto-generated from MSB Educational Institute Student List
-- Total Students: 210 (199 with email, 11 without email)

-- 1. Ensure email column exists on public.students
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- 2. Upsert students with their email (Mother email prioritized, Father fallback, NULL if none)
INSERT INTO public.students (full_name, email)
VALUES
  ('Abbas Fakhruddin Kapadia', 'nafisa_qaizarali@hotmail.com'), /* Class 7-A | Mother */
  ('Abbas Hussain Hamid', 'patan.sarrah@gmail.com'), /* Class 6-A | Mother */
  ('Abdeali Murtaza Nathdwarawala', 'sabunwala_786@hotmail.com'), /* Class 7-B | Mother */
  ('Abizar Zoaib Kutyanawala', 'burhan52508@gmail.com'), /* Class 7-B | Mother */
  ('Abizer Mufaddal Lanewala', 'lanewala@hotmail.com'), /* Class 6-B | Mother */
  ('Abizer Mustansir Colombowala', 'mustansir.colombo@gmail.com'), /* Class 7-B | Mother */
  ('Adnan Murtazahusain Marvi', 'nisreenmarvi@gmail.com'), /* Class 6-B | Mother */
  ('Aliqyaan Murtaza Jorbai', 'arwa.jobai.52@gmail.com'), /* Class 8-B | Mother */
  ('Amatullah Abbasali Lakdawala', 'sakinaabbasali52@gmail.com'), /* Class 6-C | Mother */
  ('Amatullah Hozefa Chinikamwala', 'hozefa_kool@live.com'), /* Class 7-C | Mother */
  ('Amatullah Mohammad Quettawala', 'lubaina.mohammad@gmail.com'), /* Class 6-C | Mother */
  ('Amatullah Moiz Burhani', 'taik63@hotmail.com'), /* Class 8-C | Mother */
  ('Amatullah Mu. Huzaifa Ezzy', 'fatsamu@gmail.com'), /* Class 7-C | Mother */
  ('Amatullah Mufaddal Rampurawala', 'bmrampurawala@gmail.com'), /* Class 8-C | Mother */
  ('Amatullah Shk. Murtaza Saintmarywala', 'jumanamurtaza87@gmail.com'), /* Class 6-C | Mother */
  ('Amatullah Taha Terwari', 'tahaterwari@yahoo.com'), /* Class 7-A | Mother */
  ('Amatullah Yousuf Najafwala', 'beat_of_urs_heart@hotmail.com'), /* Class 8-A | Mother */
  ('Amena Baqir Qamari', NULL), /* Class 6-A | NO EMAIL */
  ('Batool Ali Asghar Ghatila', 'aliasghar_ghatila@hotmail.com'), /* Class 8-C | Father */
  ('Batool Aliasghar Lanewala', 'zahralanewala06@gmail.com'), /* Class 6-C | Mother */
  ('Batool Aliasgher Ajmerwala', 'captivatinggirl_sagittarian@hotmail.com'), /* Class 7-A | Mother */
  ('Batool bai Yusufali bhai Ratlamwala', 'tasneemhirani@hotmail.com'), /* Class 8-C | Mother */
  ('Batool Haider Nathdwarawala', 'alify.haider5253@gmail.com'), /* Class 7-C | Mother */
  ('Batool Hussain Patanwala', 'khadija.geminie@gmail.com'), /* Class 8-A | Mother */
  ('Batool Hussain Tinwala', 'f_fairy_21@hotmail.com'), /* Class 8-A | Mother */
  ('Batool Mohammed Zariwala', 'smvarieties@gmail.com'), /* Class 7-A | Mother */
  ('Batool Mohammedhusain Ratlamwala', 'khadija.mhd52@gmail.com'), /* Class 8-C | Mother */
  ('Batool Mu. Tahir Rozanawala', 'tahirali@hotmail.com'), /* Class 7-A | Mother */
  ('Batool Mu. Yousuf Tinwala', 'tasneemjack52@gmail.com'), /* Class 6-C | Mother */
  ('Batool Mu.Murtaza Mandviwala', 'rasheedahussyn@gmail.com'), /* Class 7-C | Mother */
  ('Batool Mustafa Udaipurwala', 'murtaza.udaipur5253@gmail.com'), /* Class 7-C | Mother */
  ('Batool Sajjad Bhaijiwala', 'tasneemsajjad52@gmail.com'), /* Class 8-C | Mother */
  ('Batool Shk. Murtazaali Ferozpurwala', NULL), /* Class 8-C | NO EMAIL */
  ('Batool Taha Ujjainwala', 'taha.zulfiqar@gmail.com'), /* Class 7-A | Mother */
  ('Batool Taher Zaveri', 'tasneem.shabbir.521@gmail.com'), /* Class 6-A | Mother */
  ('Batul Hussain Lotiawala', 'ummesalam52@gmail.com'), /* Class 8-C | Mother */
  ('Burhanuddin Aamirali Gondalwala', 'fatimamansoor.52@gmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Abbas Lakdawala', 'phatyma16@gmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Abbas Rajnagarwala', 'shirinraj786110@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Adnan Khambatwala', 'fak5253@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Ali Asghar Handlawala', 'batoolaliasghar.5253@gmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Ali Asgher Kalekhan', 'ziddi_bacha52@hotmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Ali Lokhandwala', 'alifia.ali.burhanuddin@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Aliasgar Chhera wala', 'tasneemaliasgarchera@gmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Aliasghar Fakhri', 'aliasghar_79@hotmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Aun Shajapurwala', 'mariaaunali52@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Hashim Saraf', 'fine.fsh@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Hasnain Halaiwala', 'm.zab52@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Hasnain Jamnagar', 'hasnain_ibrahim@hotmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Hatim Patanwala', 'khadijahatim91@gmail.com'), /* Class 7-A | Mother */
  ('Burhanuddin Husain Jodiawala', 'hussain_sj@hotmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Hussain Mandviwala', NULL), /* Class 10-A | NO EMAIL */
  ('Burhanuddin Hussain Mithaiwala', 'arwa_kitabi@hotmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Hussain Saifee', 'luvable_luvbug18@hotmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Hussain Udaipurwala', 'hussain_leo@hotmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Huzaifa Bs Shakir', 'mubarakahs.53@gmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Huzaifa Soniwala', 'tasneemhuz89@gmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Ibrahim Kabatwala', 'ibrahim_cams@hotmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Khuzaima Mithaiwala', 'rashidakhozema123@gmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Malik ul ashtar Jetpurwala', 'tasneemmalik123@gmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Mazher Jamnagarwala', 'mariammsj@gmail.com'), /* Class 7-A | Mother */
  ('Burhanuddin Mohammad Betul', 'commercialaffairs@portgrand.com'), /* Class 8-B | Mother */
  ('Burhanuddin Mohammed Petiwala', 'jumana.ajmer@gmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Mohammed Quettawala', 'mohammadzainab04@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Mohammed Sunelwala', 'hmvirgo09@gmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Moiz Mandasorwala', 'zainy39@hotmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Mu. Abdeali Jasdanwala', 'rashujasden@gmail.com'), /* Class 7-A | Mother */
  ('Burhanuddin Mu. Fakhruddin Kaukawala', 'fakhruddins128@hotmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Mu. Hatim Dahodwala', 'hatimshkhashim@gmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Mu. Hussain Ezzy', 'fatezzy53@gmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Mu. Moiz Udaipurwala', 'alfia4u@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Mu. Taha Quettawala', 'tahaquettawala@gmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Mufaddal Munniwala', 'batool.munni@gmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Muhammad Ujjainwala', 'ummekc@yahoo.com'), /* Class 6-A | Mother */
  ('Burhanuddin Murtaza Barnagarwala', 'fatema_murtaza52@hotmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Murtaza Bhujwala', 'ideas52@hotmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Murtaza Ghaniwala', 'bohra93@yahoo.com'), /* Class 8-A | Mother */
  ('Burhanuddin Murtaza Mithaiwala', 'naqiya_mithai@hotmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Murtaza Rajkotwala', NULL), /* Class 6-B | NO EMAIL */
  ('Burhanuddin Murtaza Rampurawala', 'munira.rampurawala21@gmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin murtaza Shahjahanhotel', NULL), /* Class 6-B | NO EMAIL */
  ('Burhanuddin Murtaza Shakir', 'bsamustafa@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Mustafa Bhujwala', 'amatullahdahod@gmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Mustafa Gadriwala', 'mustafa.87@live.com'), /* Class 6-A | Mother */
  ('Burhanuddin Mustafa Lotia', 'rashmustafa120@gmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Shk. Husain Ghulam', 'sarrahusain53@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Shk. Hussain Lokhandwala', 'arwa.hunaid@gmail.com'), /* Class 7-A | Mother */
  ('Burhanuddin Shk. Huzaifa Ezzi', NULL), /* Class 6-B | NO EMAIL */
  ('Burhanuddin Shk. Moiz Halai', 'fatimamoizhalai@gmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Shk. Yousuf Jamali', 'whyjamali@yahoo.com'), /* Class 6-A | Mother */
  ('Burhanuddin Shk.Hasnain Kothari', 'fatemahasnainyousuf@gmail.com'), /* Class 7-A | Mother */
  ('Burhanuddin Yousuf Sidhpurwala', 'dashinggurl_18@hotmail.com'), /* Class 6-A | Mother */
  ('Fatema Yusufali Madhwala', 'khadijayousuf383@gmail.com'), /* Class 8-A | Mother */
  ('Fatima Murtaza Madhwala', 'murtazah21@gmail.com'), /* Class 7-C | Mother */
  ('Haider Mu. Huzaifa Dohadwala', NULL), /* Class 10-A | NO EMAIL */
  ('Hasan Mustafa Godhrawala', 'mustafaagha46@hotmail.com'), /* Class 8-A | Mother */
  ('Husain Abduttayyeb Zariwala', 'jamilaa.tayyab87@gmail.com'), /* Class 8-B | Mother */
  ('Husaina Shk. Muhammad Haryanawala', 'ht515253@gmail.com'), /* Class 7-C | Mother */
  ('Hussain Abduttayyeb Tinwala', 'batooltayyab@gmail.com'), /* Class 7-B | Mother */
  ('Hussain Adnan Junaghadwala', NULL), /* Class 7-A | NO EMAIL */
  ('Hussain Mohammad Haryanawala', 'tauras_ma_love@hotmail.com'), /* Class 8-B | Mother */
  ('Hussain Mu. Huzefa Dohadwala', NULL), /* Class 7-B | NO EMAIL */
  ('Hussain Murtaza Multanwala', 'mmurtaza90@gmail.com'), /* Class 7-B | Mother */
  ('Hussain Mustafa Bhujwala', 'amatullahdahod@gmail.com'), /* Class 6-A | Mother */
  ('Hussain Mustafa Marsiya', 'sakinaishere52@hotmail.com'), /* Class 6-A | Mother */
  ('Hussaina Huzaifa Dariwala', 'rashidahuzefa110@gmail.com'), /* Class 7-A | Mother */
  ('Hussaina Huzaifa Ujjainwala', 'zainab_seablue110@hotmail.com'), /* Class 8-C | Mother */
  ('Hussaina Mu. Abbas Sunailwala (Malak)', 'abbassunel110@yahoo.com'), /* Class 7-A | Mother */
  ('Hussaina Mu. Husain Ezzy', 'sherebanuhusain939291@gmail.com'), /* Class 6-C | Mother */
  ('Hussaina Mustafa Morbiwala', 'marrymst1@hotmail.com'), /* Class 6-C | Mother */
  ('Hussaina Tahir Topiwala', 'sakinatahir.tw@gmail.com'), /* Class 7-A | Mother */
  ('Ibrahim Mu. Abbasali Karimi', 'karimi9652@gmail.com'), /* Class 8-B | Mother */
  ('Insia Aliasghar Saverkundlawala', 'fatimasawarkundla@gmail.com'), /* Class 6-A | Mother */
  ('Insia Hussain Mandviwala', 'fatemarida52@gmail.com'), /* Class 8-C | Father */
  ('Insiya Abbas Rasheed', 'abbas_alis@hotmail.com'), /* Class 6-C | Mother */
  ('Insiya Abbasali Cyclewala', 'zahraabbasali@hotmail.com'), /* Class 7-C | Mother */
  ('Insiya Hussain Ali Talib', 'alefya.talib@gmail.com'), /* Class 7-C | Mother */
  ('Insiyah Adnan Mahuvawala', 'umehani.adnan@gmail.com'), /* Class 7-A | Mother */
  ('Insiyah Ali Akbar Rajulawala', 'umm_786@hotmail.com'), /* Class 8-A | Mother */
  ('Insiyah Shk. Murtaza Sabunwala', 'alefiamurtaza@gmail.com'), /* Class 6-A | Mother */
  ('Insiyah Shoaib Lucky', 'khadija.slucky@gmail.com'), /* Class 6-A | Mother */
  ('Insiyah Tahir Ali Kothari', 'imagn8ive@hotmail.com'), /* Class 7-C | Mother */
  ('Joon Huzaifa Multanwala', 'huzaifaali101@yahoo.com'), /* Class 7-B | Father */
  ('Joone Abizer Ghatila', 'mrs.abizer94@gmail.com'), /* Class 6-A | Mother */
  ('Jumana Hussain Ratlamwala', 'marium.jimmy@gmail.com'), /* Class 7-A | Mother */
  ('Maria Nooruddin Hyderabadwala', 'fatema.nek@gmail.com'), /* Class 6-C | Mother */
  ('Maryam Mu. Ali Akbar Valika', 'alafiavalika@yahoo.com'), /* Class 8-A | Mother */
  ('Mohammad Burhanuddin Sunailwala', 'zainabsunel@gmail.com'), /* Class 6-B | Mother */
  ('Mohammad Moiz Ratlamwala', 'aliamreliwala@gmail.com'), /* Class 6-A | Mother */
  ('Mohammed Abdulqader Sukkurwala', 'sakina.aq@hotmail.com'), /* Class 6-B | Mother */
  ('Mohammed Mufaddal Ujjainwala', 'mufazzal.a@hotmail.com'), /* Class 7-A | Mother */
  ('Mohammed Qasim Haryanawala', 'greetingbells@gmail.com'), /* Class 8-B | Mother */
  ('Mudassir Ghulamali Sistanwala', 'khadijaghulamali@gmail.com'), /* Class 8-B | Mother */
  ('Mufaddal Hussain Ratlamwala', 'hussainny5253@gmail.com'), /* Class 7-B | Mother */
  ('Mufaddal Huzaifa Pawan', 'hsp.fab.sup@hotmail.com'), /* Class 8-A | Father */
  ('Mufaddal Khozema Burhanpurwala', 'zainab.khozema.ali@gmail.com'), /* Class 7-A | Mother */
  ('Mufaddal Mohammed Paliwala', 'nafeesasiraj@gmail.com'), /* Class 8-A | Mother */
  ('Mufaddal Moiz Kapasi', 'tasneem-kapasi@hotmail.com'), /* Class 8-B | Mother */
  ('Mufaddal Mu. Huzaifa Chakera', 'sakinahuzaifa5353@gmail.com'), /* Class 8-B | Mother */
  ('Mufaddal Yusuf Burhanpurwala', 'defectedheart@gmail.com'), /* Class 6-B | Mother */
  ('Mustafa Hozefa Haryanawala', 'rashi004@hotmail.com'), /* Class 8-B | Mother */
  ('Mustansir Taher Mandviwala', 'arwatahir.mandvi@gmail.com'), /* Class 6-B | Mother */
  ('Naamah Moiz Bakoo', 'nisreenmoiz53@hotmail.com'), /* Class 8-A | Mother */
  ('Nafisa Taherali Diwan', 'murtaza_rocky52@hotmail.com'), /* Class 8-C | Mother */
  ('Naqiyah Mufaddal Ujjainwala', 'mufazzal.a@hotmail.com'), /* Class 6-C | Mother */
  ('Nisreen Hussain Sistan', 'rabab.cusp@gmail.com'), /* Class 8-A | Mother */
  ('Quaid Johar Murtaza Burhanpurwala', 'murtazamoiz_5152@live.com'), /* Class 7-B | Mother */
  ('Qusai Adnan Bharmal', 'bharmaladnan@gmail.com'), /* Class 6-A | Mother */
  ('Qusai Hussain Rajkotwala', 'khadija515253.kh@gmail.com'), /* Class 8-B | Mother */
  ('Qusai Ibrahim Petiwala', 'ibrahim_5152@hotmail.com'), /* Class 8-B | Mother */
  ('Rashida Mu. Yusuf Sharbat', 'khadija.sharbat53@gmail.com'), /* Class 8-C | Mother */
  ('Ruqaiya Juzer Lanewala', 'slw_juzer@hotmail.com'), /* Class 8-C | Mother */
  ('Ruqaiya Mohammad Lotia', 'juzerjs@gmail.com'), /* Class 6-C | Mother */
  ('Ruqaiya Mustafa Milky', 'fatemamilky11@gmail.com'), /* Class 7-C | Mother */
  ('Ruqaiyah Juzer Gadiwala', 'juzergadi@yahoo.com'), /* Class 6-C | Mother */
  ('Ruqaiyah Moiz Mandviwala', 'moizmandviwala@gmail.com'), /* Class 8-C | Mother */
  ('Ruqaiyah Murtaza Zakavi', 'murtazaqpk@gmail.com'), /* Class 6-C | Mother */
  ('Ruqaiyah Mustansir Junagadhwala', 'zainabmustansir40@gmail.com'), /* Class 6-C | Mother */
  ('Ruqaiyah Qasim Ferozpurwala', 'asma.ferozpurwala@gmail.com'), /* Class 7-C | Mother */
  ('Ruqaiyah Zainulabedin Kothari', 'urs_43v3r@live.com'), /* Class 8-A | Mother */
  ('Ruqaiyya Hussain Multanwala', 'hussainshujauddin@gmail.com'), /* Class 7-C | Mother */
  ('Saifuddin Ali Asgher Ujjainwala', 'raash_saify@live.com'), /* Class 6-B | Mother */
  ('Saifuddin Murtaza Shakir', 'saifey.integ@gmail.com'), /* Class 6-B | Mother */
  ('Sakina Abbas Icecreamwala', 'sarrahabbas94@gmail.com'), /* Class 7-A | Mother */
  ('Sakina Abbas Multanwala', 'hussainiii@gmail.com'), /* Class 6-C | Mother */
  ('Sakina Ali Abbas Gondalwala', 'a.abbas.gondal@gmail.com'), /* Class 6-C | Mother */
  ('Sakina Hasnain Gheewala', 'naqiyahhasnain53@gmail.com'), /* Class 6-C | Mother */
  ('Sakina Huzaifa Ghaniwala', 'hozefa_zakir@hotmail.com'), /* Class 8-C | Father */
  ('Sakina Khozema Jamali', 'rashidajamali5152@gmail.com'), /* Class 8-C | Mother */
  ('Sakina Mohammedhusain Ratlamwala', 'khadija.mhd52@gmail.com'), /* Class 7-C | Mother */
  ('Sakina Moiz Mandviwala', 'alburhanproducts515253@hotmail.com'), /* Class 8-C | Father */
  ('Sakina Moiz Siyalkotwala', 'fatiharyana@gmail.com'), /* Class 7-C | Mother */
  ('Sakina Mustafa Ghatila', 'ghatila@yahoo.com'), /* Class 8-C | Mother */
  ('Sakina Mustafa Jamnagarwala', 'minsiyamustafa@gmail.com'), /* Class 8-C | Mother */
  ('Sakina Mustansir Kapasi', 'mustansir92@gmail.com'), /* Class 8-C | Mother */
  ('Sakina Nasir Ali Kalawadwala', 'nasirshujauddin@gmail.com'), /* Class 7-C | Mother */
  ('Sakina Shk. Shamoil Ujjainwala', 'zainab.shamuil@gmail.com'), /* Class 8-C | Mother */
  ('Sakina Taha Mandviwala', 'fatimandvi@gmail.com'), /* Class 6-C | Mother */
  ('Sarrah Yusufali Rampurawala', 'yousufiqbal1982@gmail.com'), /* Class 7-C | Mother */
  ('Shabbir Mustansir Kapasi', 'mustansir92@gmail.com'), /* Class 8-B | Mother */
  ('Taha Aqeelhusain Dedanwala', 'insiyadedan@gmail.com'), /* Class 6-B | Mother */
  ('Taha Mohammedali Lakra wala', 'ali.muhammad_ey@hotmail.com'), /* Class 8-A | Mother */
  ('Taher Aliakbar Hamid', 'aliakberhamid@yahoo.com'), /* Class 8-B | Mother */
  ('Tahir Talib Bundiwala', 'hakimiservices@yahoo.com'), /* Class 6-B | Mother */
  ('Umm e Hani Saifuddin Marvi', 'saifmarvi@gmail.com'), /* Class 8-C | Mother */
  ('Ummehani Tahir Dhanerawala', 'cutepearl_16@hotmail.com'), /* Class 7-A | Mother */
  ('Ummulkiram Abbas Morbiwala', 'zainababbas976@gmail.com'), /* Class 6-C | Mother */
  ('Yaquob Yousuf Vasanwala', NULL), /* Class 8-A | NO EMAIL */
  ('Yousuf Huzefa Ghatila', 'huzefaghatila53@gmail.com'), /* Class 7-B | Mother */
  ('Zahra Ali Asghar Antaira', NULL), /* Class 6-C | NO EMAIL */
  ('Zahra bai Mustafa bhai Shajanhotelwala', 'taheramustafa83@gmail.com'), /* Class 7-A | Mother */
  ('Zahra Hasnain Hamid', 'insia.has@gmail.com'), /* Class 6-C | Mother */
  ('Zahra Hozefa Haryanawala', 'rashi004@hotmail.com'), /* Class 6-C | Mother */
  ('Zahra Hussain Anteria', 'ruqaiyarh3@gmail.com'), /* Class 7-C | Mother */
  ('Zahra Hussain Ratlamwala', 'marium.jimmy@gmail.com'), /* Class 7-C | Mother */
  ('Zahra Huzaifa Cyclewala', 'huzaifaanwerali@hotmail.com'), /* Class 8-A | Mother */
  ('Zahra Huzaifa Pithapurwala', 'huzaifashussain@gmail.com'), /* Class 7-A | Mother */
  ('Zahra Ibrahim Bookbinder', 'insiyah.shkshabbir@gmail.com'), /* Class 6-A | Mother */
  ('Zahra Moiz Bakoo', 'nisreenmoiz53@hotmail.com'), /* Class 8-A | Mother */
  ('Zahra Moiz Rasheed', 'sakinamoizrasheed@gmail.com'), /* Class 8-A | Mother */
  ('Zahra Mu. Hussain Najmi', 'batool5152@gmail.com'), /* Class 6-A | Mother */
  ('Zahra Mu. Murtaza Sidhpurwala', 'sakinamshikari@gmail.com'), /* Class 8-A | Mother */
  ('Zahra Mufaddal Marvi', 'mufazzal.aman@gmail.com'), /* Class 7-C | Mother */
  ('Zahra Mufazzal Pithapurwala', 'tasneem_82@hotmail.com'), /* Class 8-A | Mother */
  ('Zahra Murtaza Mithaiwala', 'fatimahatemi@gmail.com'), /* Class 8-A | Mother */
  ('Zahra Murtaza Udaipurwala', 'murxa@gmail.com'), /* Class 7-A | Mother */
  ('Zahra Mustafa Hazari', 'mustafa.hazari.52@gmail.com'), /* Class 6-C | Mother */
  ('Zahra Shabbir Godhrawala', 'shabbir_canci@hotmail.com'), /* Class 7-A | Mother */
  ('Zainab Hasnain Chandia', 'hasnain.chandia@gmail.com'), /* Class 6-C | Father */
  ('Zainab Shk. Khuzaima Rampurwala', 'fatimakhuzema.1981@attalim.net') /* Class 7-C | Mother */
ON CONFLICT (full_name) DO UPDATE
SET email = COALESCE(EXCLUDED.email, public.students.email);
