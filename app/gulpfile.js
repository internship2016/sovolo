var gulp = require('gulp');
var sass = require('gulp-ruby-sass');
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
  return sass(conf.sassPath + '/style.scss', {
      style: 'compressed',
      loadPath: ['./static/sass']
    })
    .on('error', notify.onError(function (e) {
      return "Error: " + e.message;
    }))
    .pipe(gulp.dest('./static/css'));
});

gulp.task('watch', function () {
  gulp.watch(conf.sassPath + '/**/*.scss', ['css']);
});

gulp.task('default', ['bower', 'css']);
