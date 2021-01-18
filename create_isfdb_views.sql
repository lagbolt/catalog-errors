CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `isfdb`.`author_title_series`
   AS select `isfdb`.`authors`.`author_canonical` AS `author`,`isfdb`.`titles`.`title_title` AS `title`,`isfdb`.`titles`.`series_id` AS `series`
       from ((`isfdb`.`authors` join `isfdb`.`titles`) join `isfdb`.`canonical_author` `ca`)
           where ((`ca`.`title_id` = `isfdb`.`titles`.`title_id`) and (`ca`.`author_id` = `isfdb`.`authors`.`author_id`));
           
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `isfdb`.`author_title_series_name`
    AS select `au`.`author_canonical` AS `author`,`t`.`title_title` AS `title`,`s`.`series_title` AS `series_name`
        from (((`isfdb`.`authors` `au` join `isfdb`.`canonical_author` `ca`) join `isfdb`.`titles` `t`) join `isfdb`.`series` `s`)
            where ((`t`.`series_id` = `s`.`series_id`) and (`ca`.`title_id` = `t`.`title_id`) and (`ca`.`author_id` = `au`.`author_id`));

