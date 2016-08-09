var gulp = require('gulp');
var sass = require('gulp-sass');
var notify = require('gulp-notify');
var bower = require('gulp-bower');

var conf = {
  sassPath: './static/sass',
  bowerDir: './bower_components'
};

gulp.task('bower', function () {
  return bower().pipe(gulp.dest(conf.bowerDir));
});

// Watch static/sass/style.scss,
// Compress all sass files into css
gulp.task('css', function () {
  return gulp.src(conf.sassPath + '/*.scss')
    .pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
    .pipe(gulp.dest('./static/css'));
});

gulp.task('watch', function () {
  gulp.watch(conf.sassPath + '/**/*.scss', ['css']);
});

gulp.task('default', ['bower', 'css']);
