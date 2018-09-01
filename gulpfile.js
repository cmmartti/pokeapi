
var gulp = require("gulp"); //http://gulpjs.com/
var util = require("gulp-util"); //https://github.com/gulpjs/gulp-util
var sass = require("gulp-sass"); //https://www.npmjs.org/package/gulp-sass
var autoprefixer = require('gulp-autoprefixer'); //https://www.npmjs.org/package/gulp-autoprefixer
var minifycss = require('gulp-minify-css'); //https://www.npmjs.org/package/gulp-minify-css
var rename = require('gulp-rename'); //https://www.npmjs.org/package/gulp-rename
var log = util.log;


var files = {
	sass: "static/pokemon/scss/**/*.scss"
};

gulp.task("sass", function(){
	log("Generate CSS files " + (new Date()).toString());
    gulp.src(files.sass)
		.pipe(sass({ style: 'expanded' }))
		.pipe(autoprefixer("last 3 version","safari 5", "ie 8", "ie 9"))
		.pipe(gulp.dest("static/pokemon/css/"))
		.pipe(rename({suffix: '.min'}))
		.pipe(minifycss())
		.pipe(gulp.dest("static/pokemon/css/"));
});

gulp.task("watch", function(){
    log("Watching SCSS files for modifications");
    gulp.watch(files.sass, ["sass"]);
});

gulp.task("default", ["sass"]);
