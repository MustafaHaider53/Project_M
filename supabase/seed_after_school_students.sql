-- ========================================================================
-- SEED AFTER-SCHOOL STUDENTS (94 Unique Students)
-- Sources: Mega list Shbrbd.xlsx (After School Students) + Takhteet.xlsx (2026)
-- Coverage: 94/94 Full Names | 94/94 8-digit ITS | 94/94 Emails (Mother -> Father)
-- Run this in your new After-School Supabase SQL Editor AFTER master_schema.sql
-- ========================================================================

insert into public.students (full_name, its, email)
values
  ('Abdeabiturab Hamza Mandviwala', '40212939', 'sakina.mandvi98@gmail.com'), /* Class 1-B | Mother */
  ('Abdemanaf Shk Aliasghar Maimoon', '40913200', 'mariaaliasger@gmail.com'), /* Class 10-A | Mother */
  ('Abizer Yusuf Ujjainwala', '40184356', 'yousufkika5253@hotmail.co.uk'), /* Class 3-B | Mother */
  ('Al Anwar Khuzaima Chaiwala', '50202884', 'sarrah.khozema53@gmail.com'), /* Class 2-C | Mother */
  ('Amatullah Abbasali Lakdawala', '40152535', 'sakinaabbasali52@gmail.com'), /* Class 6-C | Mother */
  ('Amatullah Hussain Halai', '50202569', 'hussaina.hh@gmail.com'), /* Class 2-C | Mother */
  ('Amatullah Moiz Burhani', '30115643', 'taik63@hotmail.com'), /* Class 8-C | Mother */
  ('Amatullah Mu. Huzaifa Ezzy', '30116160', 'fatsamu@gmail.com'), /* Class 7-C | Mother */
  ('Amatullah Mufaddal Rampurawala', '30115571', 'bmrampurawala@gmail.com'), /* Class 8-C | Mother */
  ('Amatullah Taha Anjarwala', '40914022', 'mzent_elora@hotmail.com'), /* Class 10-A | Mother */
  ('Batool Mu. Taher Sadriwala', '40160382', 'tahirsadri356@gmail.com'), /* Class 5-B | Mother */
  ('Batool Mu. Tahir Rozanawala', '40152513', 'tahirali@hotmail.com'), /* Class 7-A | Mother */
  ('Batool Murtaza Jamnagarwala', '50488459', 'aqqiqgemstone@gmail.com'), /* Class 9-B | Mother */
  ('Batool Sajjad Bhaijiwala', '40152529', 'tasneemsajjad52@gmail.com'), /* Class 8-C | Mother */
  ('Batool Taha Ujjainwala', '40915630', 'taha.zulfiqar@gmail.com'), /* Class 7-A | Mother */
  ('Batul Mu. Moiz Udaipurwala', '40499823', 'alifia4u@gmail.com'), /* Class 9-B | Mother */
  ('Burhanuddin Abbas Rajnagarwala', '50488294', 'shirinraj786110@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Abbasali Lakdawala', '40181398', 'sakinaabbasali52@gmail.com'), /* Class 4-B | Mother */
  ('Burhanuddin Aliasghar Fakhri', '40915674', 'aliasghar_79@hotmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Aliasghar Jessorwala', '40211562', 'sarrah.ajessor@gmail.com'), /* Class 1-B | Mother */
  ('Burhanuddin Aliasghar Nalwala', '40184358', 'ezzy.productions@gmail.com'), /* Class 3-A | Mother */
  ('Burhanuddin Hashim Saraf', '40160121', 'fine.fsh@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Hussain Halai', '40152334', 'hussaina.hh@gmail.com'), /* Class 5-C | Mother */
  ('Burhanuddin Huzaifa Soniwala', '40154634', 'tasneemhuz89@gmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Ibrahim Presswala', '40214514', 'lovelymaria_52@hotmail.com'), /* Class 2-B | Mother */
  ('Burhanuddin Mazher Jamnagarwala', '40499870', 'mariammsj@gmail.com'), /* Class 7-A | Mother */
  ('Burhanuddin Moiz Mandasorwala', '40152430', 'zainy39@hotmail.com'), /* Class 7-B | Mother */
  ('Burhanuddin Moiz Tinwala', '30116425', 'mariamayaz52@gmail.com'), /* Class 4-C | Mother */
  ('Burhanuddin Mu. Hatim Dahodwala', '40915627', 'hatimshkhashim@gmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Mu. Moiz Udaipurwala', '40915635', 'alfia4u@gmail.com'), /* Class 6-B | Mother */
  ('Burhanuddin Mufaddal Munniwala', '40152344', 'batool.munni@gmail.com'), /* Class 6-A | Mother */
  ('Burhanuddin Murtaza Khansaheb', '40181400', 'ruqaiyahlucky@gmail.com'), /* Class 4-A | Mother */
  ('Burhanuddin Murtaza Rampurawala', '40919856', 'munira.rampurawala21@gmail.com'), /* Class 8-B | Mother */
  ('Burhanuddin Murtazaali Halaiwala', '40172521', 'angel_dashing52@hotmail.com'), /* Class 5-C | Mother */
  ('Burhanuddin Shk. Hussain Tinwala', '40914179', 'mariam.tinwala52@gmail.com'), /* Class 9-A | Mother */
  ('Burhanuddin Shk. Moiz Halai', '30115502', 'fatimamoizhalai@gmail.com'), /* Class 8-A | Mother */
  ('Burhanuddin Yousuf Ali Lathiwala', '40915764', 'yousuf648@gmail.com'), /* Class 10-A | Mother */
  ('Fatema Mu. Abdeali Jasdenwala', '50210049', 'rashujasden@gmail.com'), /* Class 1-C | Mother */
  ('Fatima Hussain Chaiwala', '50488268', 'jamilaiqbal52@gmail.com'), /* Class 5-B | Mother */
  ('Fatima Yusufali Rampurawala', '40914169', 'yousufiqbal1982@gmail.com'), /* Class 9-A | Mother */
  ('Husaina Mu. Hussain Khambaty', '40193269', 'muniraalihussain@gmail.com'), /* Class 2-A | Mother */
  ('Husaina Yusuf Petiwala', '40211556', 'fatemausuf@gmail.com'), /* Class 1-C | Mother */
  ('Hussain Abduttayyeb Tinwala', '40154639', 'batooltayyab@gmail.com'), /* Class 7-B | Mother */
  ('Hussain Murtaza Multanwala', '40152435', 'mmurtaza90@gmail.com'), /* Class 7-B | Mother */
  ('Hussaina Abdulqadir Mundrawala', '40210237', 'sarrah.idris52@gmail.com'), /* Class 1-C | Mother */
  ('Hussaina Abizar Ghatila', '40210240', 'mrs.abizer94@gmail.com'), /* Class 2-B | Mother */
  ('Hussaina Ammar Godhrawala', '40205527', 'hassan.ind.auto@gmail.com'), /* Class 2-A | Mother */
  ('Hussaina Husain Kakal', '40181397', 'fatema.q21@gmail.com'), /* Class 4-C | Mother */
  ('Hussaina Mu. Abbas Sunailwala (Malak)', '40499861', 'abbassunel110@yahoo.com'), /* Class 7-A | Mother */
  ('Hussaina Mu. Husain Ezzy', '40160306', 'sherebanuhusain939291@gmail.com'), /* Class 6-C | Mother */
  ('Hussaina Mustafa Godhrawala', '50203859', 'mustafaagha46@gmail.com'), /* Class 3-B | Mother */
  ('Insia Huzaifa Shahjapur', '30115642', 'ymtc.fatema@gmail.com'), /* Class 10-B | Mother */
  ('Insiya Abbas Ali Udaipurwala', '40160392', 'coolgemini_52@hotmail.com'), /* Class 5-C | Mother */
  ('Insiya Ali Asghar Quettawala', '40160320', 'sarrahsaif52@gmail.com'), /* Class 5-C | Mother */
  ('Insiya Ammar Shajapurwala', '50170668', 'lovelyscorpio_14@yahoo.com'), /* Class 4-C | Mother */
  ('Insiya Hatim Mandviwala', '50191736', 'hatim.mandvi@gmail.com'), /* Class 2-A | Father */
  ('Insiya Mu. Husain Ezzy', '50183626', 'sherebanuhusain939291@gmail.com'), /* Class 4-B | Mother */
  ('Insiya Mu. Mohammad Lakdawala', '40202750', 'fatimamohdlakdawala4@gmail.com'), /* Class 2-B | Mother */
  ('Insiyah Ali Akbar Rajulawala', '40499839', 'umm_786@hotmail.com'), /* Class 8-A | Mother */
  ('Insiyah Aliasghar Mandviwala', '40184361', 'arwa.shabbir163@gmail.com'), /* Class 3-B | Mother */
  ('Insiyah Juzer Lotiawala', '40194862', 'rasheeda.khuzaima@gmail.com'), /* Class 3-B | Mother */
  ('Joon Husain Udaipurwala', '40211014', 'zainbfakh@gmail.com'), /* FS2-C | Mother */
  ('Juzer Murtaza Lotiawala', '40184360', 'smartboy_librs619@hotmail.com'), /* Class 3-B | Mother */
  ('Juzer Shabbir Kaukawala', '50210268', 'shabbir_777@hotmail.com'), /* Class 4-C | Father */
  ('Maria Nooruddin Hyderabadwala', '40160342', 'fatema.nek@gmail.com'), /* Class 6-C | Mother */
  ('Mohamed Mu. Huzaifa Lokhandwala', '50499788', 'zainab.h.lokhandwala@gmail.com'), /* Class 9-B | Mother */
  ('Mohammad Shk. Moiz Halai', '50190340', 'fatimamoizhalai@gmail.com'), /* Class 4-C | Mother */
  ('Mohammed Ammar Rangoonwala', '40212931', 'taaz64@gmail.com'), /* Class 1-C | Mother */
  ('Mohammed Mu. Abdeali Jasdenwala', '50192589', 'rashujasden@gmail.com'), /* Class 3-C | Mother */
  ('Mohammed Qasim Haryanawala', '40914186', 'greetingbells@gmail.com'), /* Class 8-B | Mother */
  ('Naqiyah Mufaddal Ujjainwala', '40160178', 'mufazzal.a@hotmail.com'), /* Class 6-C | Mother */
  ('Ruqaiya Juzer Lanewala', '30151576', 'slw_juzer@hotmail.com'), /* Class 8-C | Mother */
  ('Ruqaiyah Zainulabedin Kothari', '30115585', 'urs_43v3r@live.com'), /* Class 8-A | Mother */
  ('Ruqaiyya Hussain Multanwala', '50161178', 'hussainshujauddin@gmail.com'), /* Class 7-C | Mother */
  ('Saifuddin Abbasali Roshan shajapurwala', '40210994', 'arwa.ajmerwala@gmail.com'), /* Class 3-B | Mother */
  ('Saifuddin Ammar Godhrawala', '50171994', 'hassan.ind.auto@gmail.com'), /* Class 4-B | Mother */
  ('Saifuddin Huzaifa Shajapurwala', '30115641', 'ymtc.fatema@gmail.com'), /* Class 9-A | Mother */
  ('Saifuddin Mohammedali Marvi', '40212936', 'sakinamsaify@hotmail.com'), /* Class 1-A | Mother */
  ('Saifuddin Murtaza Shakir', '50171951', 'saifey.integ@gmail.com'), /* Class 6-B | Mother */
  ('Sakina Hasnain Gheewala', '40160104', 'naqiyahhasnain53@gmail.com'), /* Class 6-C | Mother */
  ('Sakina Murtaza Lotiawala', '40160324', 'smartboy_libra619@hotmail.com'), /* Class 4-B | Mother */
  ('Sakina Nasir Ali Kalawadwala', '40171315', 'nasirshujauddin@gmail.com'), /* Class 7-C | Mother */
  ('Sarrah Yusuf Lamuwala', '40210235', 'arwa.yousuf2792@gmail.com'), /* Class 1-C | Mother */
  ('Taher Mustafa Rawat', '40487531', 'rasheeda.rawat1@gmail.com'), /* Class 10-A | Mother */
  ('Ummehani Husain Hakimi', '40203889', 'insya.hussain@gmail.com'), /* Class 1-A | Mother */
  ('Ummehani Mustafa Burhani', '50190928', 'rvajihi52@gmail.com'), /* Class 3-C | Mother */
  ('Ummehani Tahir Dhanerawala', '30115686', 'cutepearl_16@hotmail.com'), /* Class 7-A | Mother */
  ('Yushay Hakimuddin Lokhandwala', '40210241', 'maimoontraders@hotmail.com'), /* Class 1-A | Mother */
  ('Zahra Hozefa Haryanawala', '30117362', 'rashi004@hotmail.com'), /* Class 6-C | Mother */
  ('Zahra Hussain Udaipurwala', '50191015', 'zainbfakh@gmail.com'), /* Class 3-C | Mother */
  ('Zahra Mu. Hussain Najmi', '50161714', 'batool5152@gmail.com'), /* Class 6-A | Mother */
  ('Zahra Mustafa Hazari', '40160396', 'mustafa.hazari.52@gmail.com'), /* Class 6-C | Mother */
  ('Zahra Yusuf Lamuwala', '40184372', 'arwa.yousuf2792@gmail.com'), /* Class 3-A | Mother */
  ('Zainab Hasnain Chandia', '50162454', 'hasnain.chandia@gmail.com') /* Class 6-C | Father */
on conflict (full_name) do update
set its = excluded.its,
    email = excluded.email;

-- Verify count (should return 94):
select count(*) as total_students, count(its) as with_its, count(email) as with_email from public.students;
